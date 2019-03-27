# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def create(self, vals):
        vals = self.update_vals(vals)
        vals = self._timesheet_preprocess(vals)
        return super(AccountAnalyticLine, self).create(vals)

    def update_vals(self,vals):
        if vals.get('task_id'):
            task = self.env['project.task'].browse(vals.get('task_id'))
            project_id = task.get_parent_project_id()
            if not project_id:
                raise ValidationError(_(
                    'The task should be related to a project!'))
            vals['project_id'] = project_id
        if not vals.get('employee_id'):
            if vals.get('user_id'):
                ts_user_id = vals['user_id']
            else:
                ts_user_id = self._default_user()
            vals['employee_id'] = self.env['hr.employee'].search(
                [('user_id', '=', ts_user_id)], limit=1).id
        return vals
