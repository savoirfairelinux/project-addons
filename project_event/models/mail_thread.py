# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re
from odoo import models, api, _


class MailThread(models.AbstractModel):
    _name = 'mail.thread'
    _inherit = ['mail.thread']

    @api.multi
    def _message_track(self, tracked_fields, initial):
        """ For a given record, fields to check (tuple column name, column info)
        and initial values, return a structure that is a tuple containing :

         - a set of updated column names
         - a list of changes
                    (initial value, new value, column name, column info) """
        self.ensure_one()
        changes = set()
        displays = set()
        tracking_value_ids = []
        display_values_ids = []
        TrackingValue = self.env['mail.tracking.value']
        # generate tracked_values data structure: {'col_name': {col_info,
        # new_value, old_value}}
        for col_name, col_info in tracked_fields.items():
            track_visibility = getattr(
                self._fields[col_name],
                'track_visibility',
                'onchange')
            initial_value = initial[col_name]
            new_value = getattr(self, col_name)

            if col_name == 'notes':
                col_info['string'] = _('Note')
                if new_value != initial_value:
                    new_value = _('created/modified')

            if new_value != initial_value and (
                    new_value or initial_value):
                tracking = TrackingValue.create_tracking_values(
                    initial_value, new_value, col_name, col_info)
                if tracking:
                    tracking_value_ids.append([0, 0, tracking])

                if col_name in tracked_fields:
                    changes.add(col_name)

            elif (
                new_value == initial_value and
                track_visibility == 'always' and
                col_name in tracked_fields
            ):
                tracking = TrackingValue.create_tracking_values(
                    initial_value, initial_value, col_name, col_info)
                if tracking:
                    display_values_ids.append([0, 0, tracking])
                    displays.add(col_name)

        if changes and displays:
            tracking_value_ids = display_values_ids + tracking_value_ids

        type_value = self.get_type(tracking_value_ids)

        if type_value == 'Event':
            order_fields = self.order_event_fields(tracking_value_ids)
            return changes, order_fields

        if type_value == 'Activity':
                order_fields = self.order_activity_fields(tracking_value_ids)
                return changes, order_fields

        if type_value == 'Task':
            order_fields = self.order_task_fields(tracking_value_ids)
            return changes, order_fields

        return changes, tracking_value_ids

    @staticmethod
    def get_type(tracking_values):
        type = None
        for index in range(len(tracking_values)):
            list_value = tracking_values.__getitem__(index)
            if list_value.__getitem__(2).get('field') == 'code':
                if bool(re.search(
                        "[E][V][0-9]{6}$",
                        list_value.__getitem__(2).get('new_value_char')
                )):
                    type = 'Event'
                if bool(re.search(
                        "[A][C][0-9]{6}$",
                        list_value.__getitem__(2).get('new_value_char')
                )):
                    type = 'Activity'
                if bool(re.search(
                        "[T][A][0-9]{6}$",
                        list_value.__getitem__(2).get('new_value_char')
                )):
                    type = 'Task'
        return type

    @staticmethod
    def order_event_fields(tracking_values):
        event_fields_list = [
            'name', 'code', 'responsible_id',
            'user_id', 'notes', 'state', 'partner_id'
        ]
        event_tracking_values = []
        for index in range(len(tracking_values)):
            for k in range(len(tracking_values)):
                event = tracking_values.__getitem__(k)
                if event.__getitem__(2).get('field')\
                        == event_fields_list[index]:
                    event_tracking_values.append(event)
        return event_tracking_values

    @staticmethod
    def order_activity_fields(tracking_values):
        activity_fields_list = [
            'name', 'code', 'responsible_id', 'partner_id', 'project_id',
            'notes', 'category_id', 'date_start', 'date_end', 'task_state',
            'room_id', 'resource_type', 'manager_id', 'user_id', 'client_type',
            'sector_id'
        ]
        activity_tracking_values = []
        for index in range(len(tracking_values)):
            for k in range(len(tracking_values)):
                activity = tracking_values.__getitem__(k)
                if activity.__getitem__(2).get('field')\
                        == activity_fields_list[index]:
                    activity_tracking_values.append(activity)
        return activity_tracking_values

    @staticmethod
    def order_task_fields(tracking_values):
        task_fields_list = [
            'name', 'code', 'responsible_id', 'partner_id', 'project_id',
            'notes', 'category_id', 'date_start', 'date_end', 'department_id',
            'employee_ids', 'task_state', 'room_id', 'resource_type',
            'user_id', 'client_type', 'sector_id', 'rel_date_start',
            'rel_date_end', 'report_done_required'
        ]
        task_tracking_values = []
        for x in range(len(tracking_values)):
            for k in range(len(tracking_values)):
                task = tracking_values.__getitem__(k)
                if task.__getitem__(2).get('field') == task_fields_list[x]:
                    task_tracking_values.append(task)
        return task_tracking_values
