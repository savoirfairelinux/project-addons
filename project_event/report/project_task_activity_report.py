# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from operator import itemgetter


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
    contact_label = _("Contact 1:")
    phone_label = _("Phone: ")

    @api.model
    def get_report_values(self, docids, data=None):
        today = datetime.now().date().strftime("%d-%m-%Y")
        # **self.get_activities_values(docids)[0] --> for 1 activity
        # TO DO: for multiple activities
        docs = {
            'today': today,
            **self.get_activities_values(docids)[0]
        }
        return docs

    def get_activities_values(self, docids):
        activities_docs = []
        activities = self.env['project.task'].browse(docids)
        for activity in activities:
            activities_docs.append({
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
                'name': activity.name,
                'client_id': activity.partner_id.name,
                'start': activity.date_start,
                'stop': activity.date_end,
                'tasks': self.get_task_values(activity.child_ids),
                'description': activity.description,
                'activity_notes': activity.notes,
                'remarks': self.get_departments_remarks(activity.child_ids),
            })
        return activities_docs

    def get_task_values(self, tasks):
        table_lines = []
        for task in tasks:
            for employee in task.employee_ids:
                table_lines.append({
                    'department': task.department_id.name,
                    'expected_start': task.date_start,
                    'expected_departure': task.date_end,
                    'employee': employee.name,
                    'order': task.task_order,
                })
        table_lines_sorted = sorted(
            table_lines, key=itemgetter(
                'order', 'department', 'employee'))
        return table_lines_sorted

    def get_departments_remarks(self, tasks):
        department_comments = []
        for task in tasks:
            department_comments.append((
                task.department_id.name,
                task.notes
            ))
        uniq_department_comments = self.remove_duplicate_department(
            department_comments)
        remarks = []
        for remark in uniq_department_comments:
            remarks.append({
                'department': remark[0],
                'remark': remark[1]
            })
        return remarks

    def remove_duplicate_department(self, departments=[], rest=[]):
        if len(departments) == 0:
            return rest
        else:
            item = departments.pop()
            for remark in departments:
                if remark[0] == item[0]:
                    new_remark = item[1] + remark[1]
                    item = (item[0], new_remark)
                    departments.remove(remark)
            rest.append(item)
            return self.remove_duplicate_department(departments, rest)
