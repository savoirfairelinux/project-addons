# Copyright 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import babel.dates


class ReportWeekly(models.AbstractModel):
    _name = 'report.project_resource_calendar.weekly_report_view'

    @api.model
    def get_report_values(self, docids, data=None):
        room = self.env['resource.calendar.room'].browse(
            int(data['form']['room_id'])
        )
        today = self.get_formatted_date(datetime.now())
        date_start = datetime.strptime(data['form']['date_start'], DATE_FORMAT)
        date_end = datetime.strptime(
            data['form']['date_end'], DATE_FORMAT) + timedelta(days=1)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start.strftime(DATE_FORMAT),
            'date_end': (date_end - timedelta(days=1)).strftime(DATE_FORMAT),
            'room_name': room.name,
            'docs': self.get_docs(room, data, date_start, date_end),
            'today': today,
        }

    def format_event_to_docs(self, events, docs):
        for event in events:
            docs.append({
                'name': event.name,
                'start': self.get_tz_format(event.start),
                'stop': self.get_tz_format(event.stop),
                'weekday': event.weekday_number,
                'allday': event.allday,
            })
        return docs

    def get_tz_format(self, date_str):
        return fields.Datetime.context_timestamp(self, datetime.strptime(
            date_str, '%Y-%m-%d %H:%M:%S')) .strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_events_on_period(start, stop, events):
        events_on_period = []
        for event in events:
            event_date = datetime.strptime(event.start, '%Y-%m-%d %H:%M:%S')
            if start <= event_date <= stop:
                events_on_period.append(event)
        return events_on_period

    def get_events_given_room(self, room, data):
        return self.env['calendar.event'].search([
            ('room_id', '=', room.id),
            ('recurrency', '=', data['form']['recurrency']),
            ('state', '=', data['form']['state']),
        ], order='start asc')

    def get_docs(self, room, data, date_start, date_end):
        events_filtered = self.get_events_given_room(room, data)
        events = self.get_events_on_period(
            date_start, date_end, events_filtered)
        self.review_weekdays(events)
        return self.format_event_to_docs(events, [])

    @staticmethod
    def review_weekdays(events):
        for event in events:
            event._compute_get_weekday_number()

    def get_formatted_date(self, date):
        lang = self.env['res.users'].browse(self.env.uid).lang or 'en_US'
        tz = self.env['res.users'].browse(self.env.uid).tz or 'utc'

        formatted_date = babel.dates.format_datetime(
            date,
            tzinfo=tz,
            format='EEEE dd MMMM yyyy',
            locale=lang)
        return formatted_date.capitalize()
