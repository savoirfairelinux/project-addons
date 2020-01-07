# Copyright 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
from odoo import models, fields, api


class WeeklyReportWizard(models.TransientModel):
    _name = 'weekly.report.wizard'

    date_start = fields.Date(
        string="Start Date",
        required=True,
        default=lambda self: self._get_current_monday()
    )
    date_end = fields.Date(
        string="End Date",
        required=True,
        default=lambda self: self._get_current_friday()
    )
    room_id = fields.Many2one(
        string='Room',
        comodel_name='resource.calendar.room',
        ondelete='set null',
        required=True,
    )
    recurrency = fields.Boolean(
        string='Recurrency',
        default=True,
    )
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('open', 'Confirmed'),
        ('cancelled', 'Cancelled')],
        string='Status',
        default='open',
        required=True,
    )

    @staticmethod
    def _get_current_monday():
        today = datetime.date.today()
        return today - datetime.timedelta(days=today.weekday())

    @staticmethod
    def _get_current_friday():
        today = datetime.date.today()
        return today - \
            datetime.timedelta(days=today.weekday()) + \
            datetime.timedelta(days=4)

    @api.multi
    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'room_id': self.room_id.id,
                'recurrency': self.recurrency,
                'state': self.state,
            },
        }
        return self.env.ref(
            'project_resource_calendar.weekly_report').report_action(
                self, data=data)
