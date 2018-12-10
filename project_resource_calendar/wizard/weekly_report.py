# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class ReportWeekly(models.AbstractModel):
    _name = 'report.project_resource_calendar.weekly_report_view'

    @api.model
    def get_report_values(self, docids, data=None):
        room = self.env['resource.calendar.room'].browse(
            int(data['form']['room_id'])
        )

        today = datetime.now().date().strftime("%d-%m-%Y")
        date_start = datetime.strptime(data['form']['date_start'], DATE_FORMAT)
        date_end = datetime.strptime(data['form']['date_end'], DATE_FORMAT) + timedelta(days=1)
        docs = []
        events = self.env['calendar.event'].search([
            ('room_id', '=', room.id),
            ('recurrency', '=', data['form']['recurrency']),
            ('state', '=', data['form']['state']),
            ], order='start asc')
        for event in events:
            docs.append({
                'name': event.name,
                'start': event.start,
                'stop': event.stop,
                'weekday': event.weekday,
            })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start.strftime(DATE_FORMAT),
            'date_end': (date_end - timedelta(days=1)).strftime(DATE_FORMAT),
            'room_name': room.name,
            'docs': docs,
            'today': today,
        }
