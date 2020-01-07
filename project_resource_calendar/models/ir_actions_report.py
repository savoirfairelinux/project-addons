# Copyright 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, SUPERUSER_ID, _


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.noguess
    def report_action(self, docids, data=None, config=True):
        """Override this method to hundel the special
           format of the ids of a recurrent calendar.event.

        :param docids: id/ids/browserecord of the records to print
        (if not used, pass an empty list)
        :param report_name: Name of the template to generate an action for
        """
        discard_logo_check = self.env.context.get('discard_logo_check')
        if (
            (self.env.uid == SUPERUSER_ID) and
            (
                (
                    not self.env.user.company_id.external_report_layout) or
                (not discard_logo_check and not
                 self.env.user.company_id.logo
                 )
            ) and
            config
        ):
            template = self.env.ref(
                'base.view_company_report_form_with_print')\
                if self.env.context.get(
                'from_transient_model', False) else self.env.ref(
                'base.view_company_report_form')
            return {
                'name': _('Choose Your Document Layout'),
                'type': 'ir.actions.act_window',
                'context': {'default_report_name': self.report_name,
                            'discard_logo_check': True},
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': self.env.user.company_id.id,
                'res_model': 'res.company',
                'views': [(template.id, 'form')],
                'view_id': template.id,
                'target': 'new',
            }

        context = self.env.context
        if docids:
            active_ids = []
            if isinstance(docids, models.Model):
                if isinstance(docids.ids[0], int):
                    active_ids = docids.ids
                else:
                    active_ids.append(docids.ids[0].split('-')[0])
                    event = self.env['calendar.event'].browse(active_ids)
                    if event:
                        event.current_id = docids.ids[0]
            elif isinstance(docids, int):
                active_ids = [docids]
            elif isinstance(docids, list):
                active_ids = docids
            context = dict(self.env.context, active_ids=active_ids)
        return {
            'context': context,
            'data': data,
            'type': 'ir.actions.report',
            'report_name': self.report_name,
            'report_type': self.report_type,
            'report_file': self.report_file,
            'name': self.name,
        }
