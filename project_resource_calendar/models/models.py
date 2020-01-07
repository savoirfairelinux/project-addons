# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo
from odoo import api
from odoo.osv.orm import BaseModel
import io
import uuid
from datetime import datetime
from odoo.models import fix_import_export_id_paths
from contextlib import contextmanager
import psycopg2


@api.multi
def _export_rows(self, fields, batch_invalidate=True, virtual_data=None):
    """ Export fields of the records in ``self``.

        :param fields: list of lists of fields to traverse
        :param batch_invalidate:
            whether to clear the cache for the top-level object every so often
            (avoids huge memory consumption
            when exporting large numbers of records)
        :return: list of lists of corresponding values
    """
    import_compatible = self.env.context.get('import_compat', True)
    lines = []

    def splittor(rs):
        """ Splits the self recordset in batches of 1000 (to avoid
        entire-recordset-prefetch-effects) & removes the previous batch
        from the cache after it's been iterated in full
        """
        for idx in range(0, len(rs), 1000):
            sub = rs[idx:idx + 1000]
            for rec in sub:
                yield rec
            rs.invalidate_cache(ids=sub.ids)
    if not batch_invalidate:
        def splittor(rs):
            return rs
    # both _ensure_xml_id and the splitter want to work on recordsets but
    # neither returns one, so can't really be composed...
    uniq_ids = self.browse(list(dict.fromkeys(self.ids)))
    if virtual_data:
        xids = dict(
            uniq_ids.__ensure_xml_id(
                skip=['id'] not in fields))
    else:
        xids = dict(self.__ensure_xml_id(skip=['id'] not in fields))
    # memory stable but ends up prefetching 275 fields (???)
    for record in splittor(self):
        # main line of record, initially empty
        current = [''] * len(fields)
        lines.append(current)

        # list of primary fields followed by secondary field(s)
        primary_done = []

        # process column by column
        virtual_data_current = virtual_data.pop(
            0) if virtual_data else None
        for i, path in enumerate(fields):
            if not path:
                continue

            name = path[0]
            if name in primary_done:
                continue

            if name == '.id':
                current[i] = str(record.id)
            elif name == 'id':
                xid = xids.get(record)
                assert xid, "no xid was generated for the record %s" % record
                current[i] = xid
            else:
                field = record._fields[name]
                if isinstance(field, odoo.fields.Datetime):
                    if virtual_data_current:
                        if name == 'start_datetime' or name == 'start':
                            value = virtual_data_current[0]
                        if name == 'stop_datetime' or name == 'stop':
                            value = virtual_data_current[1]
                        lines[-1][0] = '__export__.' + (record._name).replace(
                            '.', '_') + '_' + str(record.id) + '_recurrent_virtual'
                    else:
                        try:
                            value = \
                                odoo.fields.Datetime.context_timestamp(
                                    self,
                                    datetime.strptime(
                                        record[name],
                                        '%Y-%m-%d %H:%M:%S'))\
                                .strftime('%Y-%m-%d %H:%M:%S')
                        except BaseException:
                            value = ''
                else:
                    value = record[name]

                # this part could be simpler, but it has to be done this way
                # in order to reproduce the former behavior
                if not isinstance(value, BaseModel):
                    current[i] = field.convert_to_export(value, record)
                else:
                    primary_done.append(name)

                    # in import_compat mode, m2m should always be exported as
                    # a comma-separated list of xids in a single cell
                    if import_compatible and field.type == 'many2many' and len(
                            path) > 1 and path[1] == 'id':
                        xml_ids = [xid for _, xid in value.__ensure_xml_id()]
                        current[i] = ','.join(xml_ids) or False
                        continue

                    # recursively export the fields that follow name; use
                    # 'display_name' where no subfield is exported
                    fields2 = [(p[1:] or ['display_name']
                                if p and p[0] == name else []) for p in fields]
                    lines2 = value._export_rows(
                        fields2, batch_invalidate=False)
                    if lines2:
                        # merge first line with record's main line
                        for j, val in enumerate(lines2[0]):
                            if val or isinstance(val, bool):
                                current[j] = val
                        # append the other lines at the end
                        lines += lines2[1:]
                    else:
                        current[i] = False

    return lines


def __ensure_xml_id(self, skip=False):
    """ Create missing external ids for records in ``self``, and return an
        iterator of pairs ``(record, xmlid)`` for the records in ``self``.

    :rtype: Iterable[Model, str | None]
    """
    if skip:
        return ((record, None) for record in self)

    if not self:
        return iter([])

    if not self._is_an_ordinary_table():
        raise Exception(
            "You can not export the column ID of model %s, because the "
            "table %s is not an ordinary table."
            % (self._name, self._table))

    modname = '__export__'
    cr = self.env.cr
    cr.execute("""
        SELECT res_id, module, name
        FROM ir_model_data
        WHERE model = %s AND res_id in %s
    """, (self._name, tuple(self.ids)))
    xids = {
        res_id: (module, name)
        for res_id, module, name in cr.fetchall()
    }

    def to_xid(record_id):
        (module, name) = xids[record_id]
        return ('%s.%s' % (module, name)) if module else name

    # create missing xml ids
    missing = self.filtered(lambda r: r.id not in xids)
    if not missing:
        return (
            (record, to_xid(record.id))
            for record in self
        )

    xids.update(
        (r.id, (modname, '%s_%s_%s' % (
            r._table,
            r.id,
            uuid.uuid4().hex[:8],
        )))
        for r in missing
    )
    fields = ['module', 'model', 'name', 'res_id']

    @contextmanager
    def _paused_thread():
        try:
            thread = psycopg2.extensions.get_wait_callback()
            psycopg2.extensions.set_wait_callback(None)
            yield
        finally:
            psycopg2.extensions.set_wait_callback(thread)
    with _paused_thread():
        cr.copy_from(io.StringIO(
            u'\n'.join(
                u"%s\t%s\t%s\t%d" % (
                    modname,
                    record._name,
                    xids[record.id][1],
                    record.id,
                )
                for record in missing
            )),
            table='ir_model_data',
            columns=fields,
        )
    self.env['ir.model.data'].invalidate_cache(fnames=fields)

    return (
        (record, to_xid(record.id))
        for record in self
    )


@api.multi
def export_data(self, fields_to_export, raw_data=False, virtual_data=None):
    """ Export fields for selected objects

        :param fields_to_export: list of fields
        :param raw_data: True to return value in native Python type
        :rtype: dictionary with a *datas* matrix

        This method is used when exporting data via client menu
    """
    fields_to_export = [fix_import_export_id_paths(
        f) for f in fields_to_export]
    if raw_data:
        self = self.with_context(export_raw_data=True)
    return {
        'datas': self._export_rows(
            fields_to_export,
            virtual_data=virtual_data)}


BaseModel._export_rows = _export_rows
BaseModel.__ensure_xml_id = __ensure_xml_id
BaseModel.export_data = export_data
