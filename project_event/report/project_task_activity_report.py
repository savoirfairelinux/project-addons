from odoo import models, api,_
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class ReportWeekly(models.AbstractModel):
    _name = 'report.project_event.project_task_activity_report_view'

    title = _("Activity's work slips")
    print_date_text = _("Print Date")
    activity_label = _("Activity: ")
    date_label = _("Date: ")
    start_hour_label = _("Hour: ")
    end_hour_label = _("Expected End Time: ")
    number_spectators_label = _("Number of spectators: ")
    client_label = _("Client: ")
    contact_label = _("Contact 1 :")
    phone_label = _("Phone: ")

    @api.model
    def render_html(self, docids, data=None):
        import ipdb; ipdb.set_trace()
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('module.report_name')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('module.report_name', docargs)

    @api.model
    def get_report_values(self, docids, data=None):
        import ipdb
        ipdb.set_trace()
        
        today = datetime.now().date().strftime("%d-%m-%Y")
        return {

            'docs': [1],
            'today': today,
            'title': self.title,
            'print_date_text': self.print_date_text,
            'activity_label': self.activity_label,
            'date_label': self.date_label,
            'start_hour_label': self.start_hour_label,
            'end_hour_label': self.end_hour_label,
            'number_spectators_label': self.number_spectators_label,
            'client_label': self.client_label,
            'contact_label': self.contact_label,
            'phone_label': self.phone_label,    
        }

    def format_event_to_docs(self, events, docs):
        for event in events:
            docs.append({
                'name': event.name,
                'start': event.start,
                'stop': event.stop,
                'weekday': event.weekday_number,
            })
        return docs

    def get_events_on_period(self, start, stop, events):
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

    def review_weekdays(self, events):
        for event in events:
            event._get_weekday_number()
