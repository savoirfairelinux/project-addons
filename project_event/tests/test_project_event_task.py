# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import datetime, timedelta

from odoo import fields, models
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
            'responsible_id': self.project_1.responsible_id.id,
            'partner_id': self.project_1.partner_id.id,
            'category_id': self.category_1.id,
            'room_id': self.room_1.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() + timedelta(hours=4)),
        })
        self.activity_2 = self.Tasks.create({
            'name': 'Test Activity 2',
            'activity_task_type': 'activity',
            'responsible_id': self.responsible_2.id,
            'partner_id': self.partner_2.id,
            'category_id': self.category_2.id,
            'room_id': self.room_2.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(
                datetime.today() + timedelta(hours=4)
            ),
        })
        self.task_1 = self.Tasks.create({
            'name': 'Test task 1',
            'activity_task_type': 'task',
            'responsible_id': self.responsible_1.id,
            'partner_id': self.partner_1.id,
            'category_id': self.category_1.id,
            'room_id': self.room_1.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() + timedelta(hours=4)),
        })
        self.task_2 = self.Tasks.create({
            'name': 'Test Task 2',
            'activity_task_type': 'task',
            'project_id': self.project_1.id,
            'responsible_id': self.project_1.responsible_id.id,
            'partner_id': self.project_1.partner_id.id,
            'room_id': self.room_1.id,
            'parent_id': None,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
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

    def test_040_onchange_partner_id(self):
        self.activity_1.onchange_partner_id()
        self.assertEqual(
            self.activity_1.client_type.name,
            'Client Type 1')
        self.client_type_2 = self.Category_types.create({
            'name': 'Client Type 2',
        })
        self.tag_1 = self.Category.create({
            'name': 'Tag 2',
            'client_type': self.client_type_2.id,
        })
        self.partner_tag2 = self.Partners.create({
            'name': 'Partner Tag 2',
            'tag_id': self.tag_1.id,
        })
        self.activity_1.partner_id = self.partner_tag2.id
        self.activity_1.onchange_partner_id()
        self.assertEqual(
            self.activity_1.client_type.name,
            'Client Type 2')

    def test_050_compute_order_task(self):
        self.activity_1.child_ids._compute_order_task()
        self.activity_1.child_ids.date_start = fields.Datetime.to_string(
            datetime.today() + timedelta(hours=2)
        )
        self.assertEqual(
            self.activity_1.child_ids.task_order,
            120)

    def test_060_workflow_actions(self):
        res = self.activity_1.child_ids.action_option()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_reservation()
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
        res = self.activity_1.child_ids.action_request()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_request_reservation()
        self.assertEqual(
            self.activity_1.child_ids.task_state,
            'requested')

        self.assertEqual(
            reservation_event.state,
            'open')

        res = self.activity_1.child_ids.action_accept()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_accept_reservation()
        self.assertEqual(
            self.activity_1.child_ids.task_state,
            'accepted')

        self.activity_1.child_ids.action_read()
        self.assertEqual(
            self.activity_1.child_ids.task_state,
            'read')

        self.activity_1.child_ids.action_done()
        self.assertEqual(
            self.activity_1.child_ids.task_state,
            'done')

    def test_070_cancel_action(self):
        res = self.activity_1.child_ids.action_request()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_request_reservation()
        self.assertEqual(
            self.activity_1.child_ids.task_state,
            'requested')
        event_id = self.activity_1.child_ids.reservation_event_id
        calendar_event = self.env['calendar.event'].browse(
            event_id)
        self.assertEqual(calendar_event.state, 'open')
        self.activity_1.child_ids.action_cancel()
        self.assertEqual(
            self.activity_1.child_ids.task_state,
            'canceled')
        self.assertEqual(
            calendar_event.state,
            'cancelled')

    def test_080_create_activity(self):
        vals = {
            'name': 'Activity Test',
            'activity_task_type': 'activity',
            'project_id': self.project_1.id,
            'responsible_id': self.project_1.responsible_id.id,
            'partner_id': self.project_1.partner_id.id,
            'room_id': self.room_1.id,
            'parent_id': None,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
        }
        activity = self.Tasks.create(vals)
        self.assertEqual(activity.name, 'Activity Test')
        self.assertEqual(activity.activity_task_type, 'activity')
        self.assertEqual(activity.project_id.id, self.project_1.id)
        self.assertEqual(activity.responsible_id.id, self.project_1.responsible_id.id)
        self.assertEqual(activity.partner_id.id, self.project_1.partner_id.id)
        self.assertEqual(activity.room_id, self.room_1)
        self.assertEqual(activity.parent_id.id, False)
        self.assertEqual(
            datetime.strptime
            (
                activity.date_start,
                '%Y-%m-%d %H:%M:%S'
            ).replace(second=0),
            datetime.today().replace(second=0,  microsecond=0))
        self.assertEqual(
            datetime.strptime
            (
                activity.date_end,
                '%Y-%m-%d %H:%M:%S'
            ).replace(second=0, microsecond=0), 
            (datetime.today() + \
            timedelta(hours=4)).replace(second=0, microsecond=0))

    def test_090_create_orphan_task(self):
        vals = {
            'name': 'Orphan task',
            'activity_task_type': 'task',
            'partner_id': self.project_1.partner_id.id,
            'room_id': self.room_1.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
        }
        orphan_task = self.Tasks.create(vals)
        self.assertEqual(
            orphan_task.name,
            'Orphan task'
        )

    def test_100_compute_complete_name_activity(self):
        self.assertEqual(self.activity_1.name, 'Test Activity 1')

    def test_110_compute_complete_name_task(self):
        complete_name = '%s / %s' % (self.task_2.code, self.task_2.name)
        self.assertEqual(self.task_2.complete_name, complete_name)

    def test_120_onchange_parent_id(self):
        self.task_1.parent_id = self.activity_2
        self.assertEqual(self.task_1.responsible_id.name, 'Responsible 1')
        self.assertEqual(self.task_1.partner_id.name, 'Partner 1')
        self.assertEqual(self.task_1.category_id.name, 'Category 1')
        self.task_1.onchange_parent_id()
        self.assertEqual(self.task_1.responsible_id.name, 'Responsible 2')
        self.assertEqual(self.task_1.partner_id.name, 'Partner 2')
        self.assertEqual(self.task_1.category_id.name, 'Category 2')
        self.task_1.parent_id = self.activity_1
        self.assertEqual(self.task_1.responsible_id.name, 'Responsible 2')
        self.assertEqual(self.task_1.partner_id.name, 'Partner 2')
        self.assertEqual(self.task_1.category_id.name, 'Category 2')
        self.task_1.onchange_parent_id()
        self.assertEqual(self.task_1.responsible_id.name, 'Responsible 1')
        self.assertEqual(self.task_1.partner_id.name, 'Partner 1')
        self.assertEqual(self.task_1.category_id.name, 'Category 1')
