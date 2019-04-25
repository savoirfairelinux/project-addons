# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class DoubleBookingValidationWiz(models.TransientModel):
    """Wizard Reservation Confirmation"""
    _name = 'doublebooking.validation.wiz'
    _description = __doc__

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
        for activity in self.event_id.task_ids:
            activity.do_reservation()
        if self.event_id.state == 'accepted':
            self.event_id.send_message('option')
        self.event_id.write({'state': 'option'})
