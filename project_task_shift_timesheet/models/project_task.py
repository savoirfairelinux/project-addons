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
        main_task = self.get_main_task()
        vals.pop('project_id', None)
        vals.pop('shift_timesheet', None)
        temp = []
        if 'task_state' in vals:
            return False
        if 'child_ids' in vals:
            temp = vals.pop('child_ids')
        main_task = main_task.write(vals)
        if temp:
            vals['child_ids'] = temp
        return main_task
