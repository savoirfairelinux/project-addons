# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ReservationValidationWiz(models.TransientModel):
    """Wizard Reservation Confirmation"""
    _name = 'reservation.validation.wiz'
    _description = __doc__

    task_id = fields.Many2one(
        'project.task',
        string='Task',
    )
    message = fields.Html(
        string='Message',
    )

    @api.multi
    def confirm_reservation(self):
        self.ensure_one()
        if self.task_id.activity_task_type == 'task':
            self.task_id.draft_resources_reservation()
            if self.task_id.task_state not in ['option', 'done']:
                self.task_id.send_message('option')
        if self.task_id.activity_task_type == 'activity':
            for child in self.task_id.child_ids:
                child.draft_resources_reservation()
                if child.task_state not in ['option', 'done']:
                    child.send_message('option')
            self.task_id.send_message('option')
        self.task_id.write({'task_state': 'option'})
