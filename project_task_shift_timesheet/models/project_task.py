# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class Task(models.Model):
    _inherit = ['project.task']

    shift_timesheet = fields.One2many(
        'shift.timesheet',
        'activity_id',
    )

    @api.multi
    def write_main_task(self, vals):
        if 'shift_timesheet' in vals:
            return
        return super(Task, self).write_main_task(vals)

    def verify_field_access_activity_write(self, vals):
        if self.task_state == 'approved' and self.user_has_groups(
                'project_event.group_project_event_user') and not \
                self.user_has_groups(
                'project_event.group_project_event_editor'):
            allowed_keys = ('spectators', 'notes', 'shift_timesheet')
            if not set(vals).issubset(allowed_keys):
                raise AccessError(
                    _('You can only edit field notes, spectators and timesheet'))
