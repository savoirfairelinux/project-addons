# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class DoubleTaskValidationWiz(models.TransientModel):
    """Wizard Reservation Confirmation"""
    _name = 'double.task.validation.wiz'
    _description = __doc__

    task_id = fields.Many2one(
        'project.task',
        string='Task',
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

    @api.multi
    def confirm_update(self):
        self.task_id.write({'date_start': self.start_date,
                            'date_end': self.end_date})

    @api.multi
    def confirm_cancel(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
