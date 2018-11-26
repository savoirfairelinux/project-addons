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
    event_id = fields.Many2one(
        'project.project',
        string='Event',
    )
    message = fields.Html(
        string='Message',
    )

    @api.multi
    def confirm_reservation(self):
        if self.task_id:
            self.task_id.do_reservation()
        else:
            for activity in self.event_id.task_ids:
                activity.do_reservation()
            self.event_id.write({'state': 'option'})
