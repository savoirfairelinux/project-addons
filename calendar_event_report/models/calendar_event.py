# Copyright 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import babel.dates
from odoo import fields, models
from datetime import datetime


class CalendarEvent(models.Model):

    _inherit = 'calendar.event'

    recurrency_icon = fields.Integer(
        compute='_compute_recurrency_icon'
    )
    formated_start = fields.Datetime(
        compute='_compute_formated_date_for_report',
    )
    formated_stop = fields.Datetime(
        compute='_compute_formated_date_for_report',
    )

    def _compute_formated_date_for_report(self):
        self.formated_start = self._compute_formated(self.start_datetime)
        self.formated_stop = self._compute_formated(self.stop_datetime)

    def _compute_formated(self, date):
        formated_date = self.format_date(
            date,
            format_str='Y-MM-dd HH:mm:SS')
        return datetime.strptime(
            formated_date, '%Y-%m-%d %H:%M:%S')

    def format_date(self, date_to_format, format_str='dd-MMMM-yyyy HH:mm:ss'):
        lang = self.env['res.users'].browse(self.env.uid).lang or 'en_US'
        tz = self.env['res.users'].browse(self.env.uid).tz or 'utc'
        if not isinstance(date_to_format, datetime):
            if self.allday:
                date_to_format = datetime.strptime(
                    date_to_format, '%Y-%m-%d'
                )
            else:
                date_to_format = datetime.strptime(
                    date_to_format, '%Y-%m-%d %H:%M:%S'
                )
        return babel.dates.format_datetime(
            date_to_format,
            tzinfo=tz,
            format=format_str,
            locale=lang)

    def get_formatted_date(self, date_to_format, field_name, format):
        recurrent = None
        if self.recurrency:
            recurrent = self.env['calendar.event'].browse(self.current_id)
        if format:
            if field_name == 'start_date':
                if recurrent:
                    date_to_format = recurrent.start_date
                else:
                    date_to_format = self.start_date
            elif field_name == 'start_datetime':
                if recurrent:
                    date_to_format = recurrent.start_datetime
                else:
                    date_to_format = self.start_datetime
        formatted_date = self.format_date(date_to_format, 'EEEE dd MMMM yyyy')
        return formatted_date.capitalize()

    def print_calendar_report(self):
        return self.env.ref(
            'calendar_event_report.calendar_event_report'

        ).report_action(self)
