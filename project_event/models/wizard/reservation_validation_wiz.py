# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ReservationValidationWiz(models.TransientModel):
    """Wizard Reservation Confirmation"""
    _name = 'reservation.validation.wiz'
    _description = __doc__

    subject_id = fields.Many2one(
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
    action = fields.Selection(
        [
            ('option', 'Option'),
            ('request', 'Request'),
            ('accept', 'Accept'),
        ],
        string='Action',
    )

    @api.multi
    def confirm_reservation(self):
        if self.subject_id:
            self.subject_id.do_reservation()
        else:
            for activity in self.event_id.subject_ids:
                activity.do_reservation()
            if self.event_id.state == 'accepted':
                self.event_id.send_message('option')
            self.event_id.write({'state': 'option'})

    @api.multi
    def confirm_request_reservation(self):
        if self.subject_id:
            self.subject_id.confirm_reservation()

    @api.multi
    def confirm_accept_reservation(self):
        if self.subject_id:
            self.subject_id.confirm_accept_reservation()
        else:
            self.event_id.confirm_accept_reservation()
