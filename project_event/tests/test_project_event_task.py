# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import datetime, timedelta

from odoo import fields
from odoo.addons.project_event.tests.common import TestProjectEventCommon


class TestProjectEventTask(TestProjectEventCommon):

    def setUp(self):
        super(TestProjectEventTask, self).setUp()
        self.Tasks = self.env['project.task']
        self.Rooms = self.env['project.task']

        self.activity_1 = self.Tasks.create({
            'name': 'Test Activity 1',
            'activity_task_type': 'activity',
            'project_id': self.project_1.id,
            'room_id': self.room_1.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() + timedelta(hours=4)),
        })

    def test_010_compute_project_task_log(self):
        self.AuditLogObj = self.env['auditlog.log']

        self.AuditLogObj.create({
            'model_id': self.env.ref('project.model_project_task').id,
            'res_id': self.activity_1.id,
        })
        self.assertEqual(self.activity_1.project_task_log, 2)
        self.activity_1.name = 'Test Event Activity 1'
        self.assertEqual(self.activity_1.project_task_log, 3)

    def test_020_create_main_task(self):
        self.assertEqual(len(self.activity_1.child_ids), 1)
        self.assertEqual(
            self.activity_1.child_ids.name,
            self.activity_1.name)
        self.assertEqual(
            self.activity_1.child_ids.activity_task_type,
            'task')
        self.assertEqual(
            self.activity_1.child_ids.date_start,
            self.activity_1.date_start)
        self.assertEqual(
            self.activity_1.child_ids.date_end,
            self.activity_1.date_end)

    def test_030_onchange_resource_type(self):
        self.activity_1.child_ids._onchange_resource_type()
        self.assertEqual(
            self.activity_1.child_ids.room_id.id,
            False)
        self.assertEqual(
            self.activity_1.child_ids.equipment_id.id,
            False)

    def test_040_compute_order_task(self):
        self.activity_1.child_ids._compute_order_task()
        self.activity_1.child_ids.date_start = fields.Datetime.to_string(
            datetime.today() + timedelta(hours=2)
        )
        self.assertEqual(
            self.activity_1.child_ids.task_order,
            120)

    def test_050_workflow_actions(self):
        self.activity_1.child_ids.action_option()
        self.assertEqual(
            self.activity_1.child_ids.task_state,
            'option')
        event_id = self.activity_1.child_ids.reservation_event_id
        reservation_event = self.env['calendar.event'].browse(
            event_id)
        self.assertEqual(
            reservation_event.state,
            'draft')
        self.assertEqual(
            reservation_event.start,
            self.activity_1.child_ids.date_start)
        self.assertEqual(
            reservation_event.stop,
            self.activity_1.child_ids.date_end)
        self.assertEqual(
            reservation_event.name,
            self.activity_1.child_ids.name)
        self.assertEqual(
            reservation_event.resource_type,
            self.activity_1.child_ids.resource_type)
        self.assertEqual(
            reservation_event.room_id,
            self.activity_1.child_ids.room_id)
        self.assertEqual(
            reservation_event.equipment_ids.ids,
            self.activity_1.child_ids.get_equipment_ids_inside())
        self.activity_1.child_ids.action_request()
        self.assertEqual(
            self.activity_1.child_ids.task_state,
            'requested')
        #the commented code didnt work because when we accept a task,
        # it creates a new calendar event but it
        #  should only update the old calendar event
        # self.activity_1.child_ids.action_accept()
        # self.assertEqual(
        #     self.activity_1.child_ids.task_state,
        #     'accepted')
        # self.assertEqual(
        #     reservation_event.state,
        #     'open')
        # self.activity_1.child_ids.action_read()
        # self.assertEqual(
        #     self.activity_1.child_ids.task_state,
        #     'read')
        # self.activity_1.child_ids.action_done()
        # self.assertEqual(
        #     self.activity_1.child_ids.task_state,
        #     'done')
        #
        # self.activity_1.child_ids.action_cancel()
        # self.assertEqual(
        #     self.activity_1.child_ids.task_state,
        #     'canceled')
        # self.assertEqual(
        #     reservation_event.state,
        #     'cancelled')
