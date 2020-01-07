# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, models, tools


class MailTracking(models.Model):
    _name = 'mail.tracking.value'
    _inherit = ['mail.tracking.value']

    @api.model
    def create_tracking_values(
            self,
            initial_value,
            new_value,
            col_name,
            col_info):
        tracked = True
        values = {
            'field': col_name,
            'field_desc': col_info['string'],
            'field_type': col_info['type']}
        if col_info['type'] in [
            'integer',
            'float',
            'char',
            'text',
            'datetime',
                'monetary']:
            values.update({
                'old_value_%s' % col_info['type']: initial_value,
                'new_value_%s' % col_info['type']: new_value
            })
        elif col_info['type'] == 'html':
            col_info['type'] = 'char'
            values.update({
                'new_value_%s' % col_info['type']: new_value
            })
        elif col_info['type'] == 'date':
            values.update(
                {
                    'old_value_datetime': initial_value and datetime.strftime(
                        datetime.combine(
                            datetime.strptime(
                                initial_value,
                                tools.DEFAULT_SERVER_DATE_FORMAT),
                            datetime.min.time()),
                        tools.DEFAULT_SERVER_DATETIME_FORMAT) or False,
                    'new_value_datetime': new_value and datetime.strftime(
                        datetime.combine(
                            datetime.strptime(
                                new_value,
                                tools.DEFAULT_SERVER_DATE_FORMAT),
                            datetime.min.time()),
                        tools.DEFAULT_SERVER_DATETIME_FORMAT) or False,
                })
        elif col_info['type'] == 'boolean':
            values.update({
                'old_value_integer': initial_value,
                'new_value_integer': new_value
            })
        elif col_info['type'] == 'selection':
            values.update({
                'old_value_char': initial_value and dict(
                    col_info['selection'])[initial_value] or '',
                'new_value_char': new_value and dict(
                    col_info['selection'])[new_value] or ''
            })
        elif col_info['type'] == 'many2one':
            values.update({
                'old_value_integer': initial_value and initial_value.id or 0,
                'new_value_integer': new_value and new_value.id or 0,
                'old_value_char': initial_value and
                initial_value.name_get()[0][1] or '',
                'new_value_char': new_value and
                new_value.name_get()[0][1] or ''
            })
        elif col_info['type'] == 'many2many':
            values.update({
                'old_value_char': initial_value and list(
                    map(lambda x: x.name, initial_value)) or '',
                'new_value_char': new_value and list(
                    map(lambda x: x.name, new_value)) or ''
            })
        else:
            tracked = False

        if tracked:
            return values
        return {}
