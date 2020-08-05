import json
from odoo import http
from datetime import datetime
from datetime import timedelta
from odoo.http import Response


class GesteveApi(http.Controller):
    @http.route('/api/calendar/events', auth='public',
                type='http', method=['GET'], cors='*')
    def get_calendar_events(self, **kw):
        headers = {'Content-Type': 'application/json'}
        try:
            start_date = kw['start_date']
            end_date = kw['end_date']
            room_name = kw['room']
            room = http.request.env['resource.calendar.room'].sudo().search([
                ('name', '=', room_name)])
            if room:
                calendar_events = http.request.env['calendar.event'] \
                    .sudo().search([('room_id', '=', room.id),
                                    ('start_datetime',
                                     '>=', start_date),
                                    ('stop_datetime', '<=', end_date)])

            data = []
            for event in calendar_events:
                event_dict = {}
                event_dict['id'] = event.id
                event_dict['title'] = event.name + ((
                    '\n' + event.room_id.name) if isinstance(event.room_id.name, str)
                    else 'No Room')
                event_dict['allDay'] = event.allday

                if event.allday:
                    event_dict['start'] = event.start_date
                    stop_date = datetime.strptime(
                        event.stop_date, '%Y-%m-%d') + timedelta(days=1)
                    event_dict['end'] = stop_date.strftime('%Y-%m-%d')
                else:
                    event_dict['start'] = self.format_date(
                        event.start_datetime) if isinstance(
                        event.start_datetime, str) else event.start_datetime
                    event_dict['end'] = self.format_date(
                        event.stop_datetime) if isinstance(
                        event.start_datetime, str) else event.stop_datetime

                event_dict['backgroundColor'] = event.color
                event_dict['textColor'] = event.font_color
                event_dict['room_id'] = event.room_id.id if event.room_id else 'Null'
                event_dict['room_name'] = event.room_id.name if isinstance(
                    event.room_id.name, str) else 'Null'
                data.append(event_dict)

            body = {'results': {'code': 200, 'message': data}}

            return Response(json.dumps(body), headers=headers)
        except BaseException:

            body = {'results': {'code': 500,
                                'message': 'Error missing parameters'}}

            return Response(json.dumps(body), headers=headers)

    def format_date(self, date):
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime(
            '%Y-%m-%dT%H:%M:%SZ')
