# © 2019 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _, fields
from datetime import datetime
from operator import itemgetter


class ReportWeekly(models.AbstractModel):
    _name = 'report.project_event.project_task_activity_report_view'

    @api.model
    def get_report_values(self, docids, data=None):
        today = self.get_tz_format(datetime.now().
                                   strftime("%Y-%m-%d %H:%M:%S"))
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
                'name': activity.name,
                'activity_code': activity.code,
                'client_id': activity.partner_id.name,
                'client_phone': activity.partner_id.phone,
                'client_type': activity.client_type,
                'start': self.get_tz_format(activity.date_start),
                'stop': self.get_tz_format(activity.date_end),
                'spectators': activity.spectators,
                'tasks': self.get_task_values(activity.child_ids),
                'tasks_uniq_dep_and_employee':
                self.get_task_values_with_uniq_department_and_employee(
                    activity.child_ids),
                'description': activity.description,
                'activity_notes': activity.notes,
                'remarks': self.get_departments_remarks(activity.child_ids),
                'descriptions': self.get_departments_descriptions(activity
                                                                  .child_ids),
                'tasks_details': self.get_tasks_details(activity.child_ids),
                'client_child_contacts': activity.partner_id.child_ids,
                'activity_plans': activity.plan_ids,
                'task_plans': self.get_task_plans(activity),
            })
        return activities_docs

    def get_tz_format(self, date_str):
        return fields.Datetime.context_timestamp(self, datetime.strptime(
            date_str, '%Y-%m-%d %H:%M:%S')) .strftime('%Y-%m-%d %H:%M:%S')

    def get_task_values(self, tasks):
        table_lines = []
        for task in tasks:
            for employee in task.employee_ids:
                table_lines.append({
                    'department': task.department_id.name,
                    'expected_start': self.get_tz_format(task.date_start),
                    'employee': employee.name,
                    'service': task.service_id.name if task.service_id else '',
                    'order': task.task_order,
                    'real_start':
                    self.get_tz_format(task.real_date_start) if (
                        task.real_date_start) else '',
                })
        table_lines_sorted = sorted(
            table_lines, key=itemgetter(
                'order', 'department', 'employee'))
        return table_lines_sorted

    def get_task_values_with_uniq_department_and_employee(self, tasks):
        table_lines_sorted = self.get_task_values(tasks)
        return self.get_different_department_and_employee(table_lines_sorted)

    @staticmethod
    def get_different_department_and_employee(sorted_list):
        done = set()
        result = []
        for element in sorted_list:
            if (element['employee'], element['department']) not in done:
                done.add((element['employee'], element['department']))
                result.append(element)
        return result

    def get_tasks_details(self, tasks):
        tasks_details = []
        for task in tasks:
            if task.resource_type == 'room' and task.room_id:
                resources_list = _('Room: ') + task.room_id.name + '<br/>' +\
                    _('Equipment: <br/>')
                tab = '&nbsp;&nbsp;&nbsp;&nbsp;'
                for instrument in task.room_id.instruments_ids:
                    resources_list += tab + instrument.name + '<br/>'
                tasks_details.append({
                    'task': task.name,
                    'resource_type': 'Room',
                    'resource': resources_list,
                })
            elif task.resource_type == 'equipment' and task.equipment_id and \
                    (task.equipment_id.category_type == 'instrument' or
                     task.equipment_id.category_type == 'equipment'):
                tasks_details.append({
                    'task': task.name,
                    'resource_type': task.equipment_id.category_type.title(),
                    'resource': task.equipment_id.name,
                })
            else:
                tasks_details.append({
                    'task': task.name,
                    'resource_type': 'NA',
                    'resource': 'NA'
                })
            tasks_details[-1].update({
                'expected_start': self.get_tz_format(task.date_start),
                'expected_end': self.get_tz_format(task.date_end),
                'real_start': (
                    self.get_tz_format(task.real_date_start)
                    if task.real_date_start
                    else ''),
                'real_end': (
                    self.get_tz_format(task.real_date_end)
                    if task.real_date_end
                    else ''),
                'duration': task.actual_total_time,
            })

        tasks_details_sorted = sorted(
            tasks_details, key=itemgetter(
                'expected_start'))

        return tasks_details_sorted

    def get_departments_descriptions(self, tasks):
        department_descriptions = []
        for task in tasks:
            if not task.is_main_task:
                department_descriptions.append((
                    task.department_id.name,
                    task.description
                ))
        uniq_department_comments = self.remove_duplicate_department(
            department_descriptions, [])
        descriptions = []
        for description in uniq_department_comments:
            descriptions.append({
                'department': description[0],
                'description': description[1]
            })
        return descriptions

    def get_departments_remarks(self, tasks):
        department_comments = []
        for task in tasks:
            if not task.is_main_task:
                department_comments.append((
                    task.department_id.name,
                    task.notes
                ))
        uniq_department_comments = self.remove_duplicate_department(
            department_comments, [])
        remarks = []
        for remark in uniq_department_comments:
            remarks.append({
                'department': remark[0],
                'remark': remark[1]
            })
        return remarks

    def remove_duplicate_department(self, departments=None, rest=None):
        if not departments:
            departments = []
        if not rest:
            rest = []
        if len(departments) == 0:
            return rest
        else:
            item = departments.pop()
            departments_loop = departments.copy()
            for remark in departments_loop:
                if remark[0] == item[0]:
                    new_remark = item[1] + remark[1]
                    item = (item[0], new_remark)
                    departments.remove(remark)
            rest.append(item)
            return self.remove_duplicate_department(departments, rest)

    def get_task_plans(self, activity):
        plans = []
        for task in activity.child_ids:
            if not task.is_main_task:
                plans += task.plan_ids.ids
        return self.env['project.event.plan'].browse(plans)
