# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class DoubleBookingValidationWiz(models.TransientModel):
    """Wizard Reservation Confirmation"""
    _name = 'doublebooking.validation.wiz'
    _description = __doc__

    event_id = fields.Many2one(
        'calendar.event',
        string='Event',
    )
    message = fields.Html(
        string='Message',
    )

    start_date = fields.Datetime(
        string='Starting Date'
    )

    end_date = fields.Datetime(
        string='Ending Date'
    )

    r_start_date = fields.Datetime(
        string='Rollback Starting Date'
    )

    r_end_date = fields.Datetime(
        string='Rollback Ending Date'
    )

    @api.multi
    def confirm_update(self):
        self.event_id.write({'start_datetime': self.start_date,
                             'stop_datetime': self.end_date})


    @api.multi
    def confirm_cancel(self):
        self.event_id.write({'start_datetime': self.r_start_date,
                             'stop_datetime': self.r_end_date})
