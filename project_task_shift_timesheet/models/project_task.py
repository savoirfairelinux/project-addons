# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class Task(models.Model):
    _inherit = ['project.task']

    shift_timesheet = fields.One2many(
        'shift.timesheet',
        'activity_id',
    )

    @api.multi
    def write_main_task(self, vals):
        vals.pop('project_id', None)
        return super(Task, self).write_main_task(vals)
