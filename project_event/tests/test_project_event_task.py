# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import datetime, timedelta

from odoo import fields, models
from odoo.addons.project_event.tests.common import TestProjectEventCommon


class TestProjectEventTask(TestProjectEventCommon):

    def setUp(self):
        super(TestProjectEventTask, self).setUp()

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
        self.project_1._onchange_partner_id()
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
            'Client Type 1')

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
            self.activity_1.child_ids.complete_name)
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
        self.assertEqual(
            activity.responsible_id.id,
            self.project_1.responsible_id.id)
        self.assertEqual(activity.partner_id.id, self.project_1.partner_id.id)
        self.assertEqual(activity.room_id, self.room_1)
        self.assertEqual(activity.parent_id.id, False)
        self.assertEqual(
            datetime.strptime
            (
                activity.date_start,
                '%Y-%m-%d %H:%M:%S'
            ).replace(second=0),
            datetime.today().replace(second=0, microsecond=0))
        self.assertEqual(
            datetime.strptime
            (
                activity.date_end,
                '%Y-%m-%d %H:%M:%S'
            ).replace(second=0, microsecond=0),
            (datetime.today() +
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

    def test_130_compute_task_state_visible(self):
        self.assertEqual(self.task_1.task_state, 'draft')
        self.task_1.write({'task_state': 'done'})
        self.assertEqual(
            self.task_1.task_state_report_done_required, 'done')
        self.assertEqual(
            self.task_1.task_state_report_not_done_required, 'done')

    def test_140_create_new_activity_with_tasks(self):
        activity_vals = {
            'category_id': self.category_1.id,
            'responsible_id': self.partner_2.id,
            'notes': '<p><br></p>',
            'room_id': False,
            'date_start': '2018-12-21 17:39:27',
            'name': 'A1',
            'sector_id': False,
            'client_type': False,
            'child_ids': [[0, 'virtual_584',
                           {'responsible_id': self.partner_2.id,
                            'parent_id': False,
                            'employee_ids': [[6, False, []]],
                            'task_state': 'draft',
                            'sector_id': False,
                            'department_id': self.department_1.id,
                            'equipment_id': False,
                            'date_end': '2018-12-21 17:39:44',
                            'date_start': '2018-12-21 16:40:44',
                            'task_state_report_not_done_required': 'draft',
                            'report_done_required': False,
                            'asterisk_validate_record': False,
                            'description': '<p><br></p>',
                            'category_id': self.category_1.id,
                            'preceding_task_ids': [[6, False, []]],
                            'notes': '<p><br></p>',
                            'task_order': -58,
                            'succeeding_task_ids': [[6, False, []]],
                            'name': 'Task IN 1',
                            'client_type': False,
                            'activity_task_type': 'task',
                            'room_id': False,
                            'partner_id': False,
                            'resource_type': 'user',
                            'task_state_report_done_required': 'draft',
                            'project_id': False}]],
            'activity_task_type': 'activity',
            'task_state': 'draft',
            'partner_id': False,
            'description': '<p><br></p>',
            'date_end': '2018-12-21 18:40:27',
            'project_id': False
        }

        activity_with_task = self.Tasks.create(activity_vals)
        self.assertEqual(
            len(activity_with_task.child_ids), 2
        )

    def test_150_update_reservation_event(self):
        self.client_type_original = self.Category_types.create({
            'name': 'Client Type Original',
        })
        self.category_original = self.Task_category.create({
            'name': 'Category Original',
        })
        self.tag_original = self.Category.create({
            'name': 'Tag Original',
            'client_type': self.client_type_1.id,
        })
        self.partner_original = self.Partners.create({
            'name': 'Partner Original',
            'tag_id': self.tag_original.id,
        })
        self.department_original = self.Department.create({
            'name': 'Department Original'
        })
        self.room_original = self.Rooms.create({
            'name': 'Room Original',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.category_new = self.Task_category.create({
            'name': 'Category New',
        })
        self.department_new = self.Department.create({
            'name': 'Department New'
        })
        self.sector_new = self.Sector.create({
            'name': 'Sector New'
        })
        self.room_new = self.Rooms.create({
            'name': 'Room New',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        name_new = 'New_Activity_1'

        activity_vals = {
            'category_id': self.category_original.id,
            'responsible_id': self.partner_original.id,
            'notes': '<p><br></p>',
            'room_id': self.room_original.id,
            'date_start': '2018-12-21 17:39:27',
            'name': 'Original_Activity_1',
            'sector_id': False,
            'client_type': False,
            'child_ids': [[0, 'virtual_584',
                           {'responsible_id': self.partner_original.id,
                            'parent_id': False,
                            'employee_ids': [[6, False, []]],
                            'task_state': 'draft',
                            'sector_id': False,
                            'department_id': self.department_original.id,
                            'equipment_id': False,
                            'date_end': '2018-12-21 17:39:44',
                            'date_start': '2018-12-21 16:40:44',
                            'task_state_report_not_done_required': 'draft',
                            'report_done_required': False,
                            'asterisk_validate_record': False,
                            'description': '<p><br></p>',
                            'category_id': self.category_original.id,
                            'preceding_task_ids': [[6, False, []]],
                            'notes': '<p><br></p>',
                            'task_order': -58,
                            'succeeding_task_ids': [[6, False, []]],
                            'name': 'Task IN 1',
                            'client_type': False,
                            'activity_task_type': 'task',
                            'room_id': self.room_original.id,
                            'partner_id': False,
                            'resource_type': 'user',
                            'task_state_report_done_required': 'draft',
                            'project_id': False}]],
            'activity_task_type': 'activity',
            'task_state': 'draft',
            'partner_id': False,
            'description': '<p><br></p>',
            'date_end': '2018-12-21 18:40:27',
            'project_id': False
        }
        activity_plus_task = self.Tasks.create(activity_vals)
        self.assertEqual(
            activity_plus_task.name,
            'Original_Activity_1')
        self.assertEqual(
            activity_plus_task.room_id.name,
            'Room Original')
        self.assertEqual(
            activity_plus_task.child_ids[0].category_id.name,
            'Category Original')
        self.assertEqual(
            activity_plus_task.child_ids[0].room_id.name,
            'Room Original')

        activity_plus_task.name = name_new
        self.assertEqual(
            activity_plus_task.name,
            'New_Activity_1')
        date_start_new = '2019-12-12 11:11:11'
        date_end_new = '2019-12-12 12:12:12'
        activity_plus_task.child_ids[0].date_start = date_start_new
        self.assertEqual(
            activity_plus_task.child_ids[0].date_start,
            '2019-12-12 11:11:11')
        activity_plus_task.child_ids[0].date_end = date_end_new
        self.assertEqual(
            activity_plus_task.child_ids[0].date_end,
            '2019-12-12 12:12:12')
        activity_plus_task.child_ids[0].department_id = self.department_new
        activity_plus_task.child_ids[0].category_id = self.category_new
        activity_plus_task.child_ids[0].room_id = self.room_new
        activity_plus_task.child_ids[0].sector_id = self.sector_new
        self.assertEqual(
            activity_plus_task.child_ids[0].department_id.name,
            'Department New')
        self.assertEqual(
            activity_plus_task.child_ids[0].category_id.name,
            'Category New')
        self.assertEqual(
            activity_plus_task.child_ids[0].room_id.name,
            'Room New')
        self.assertEqual(
            activity_plus_task.child_ids[0].sector_id.name,
            'Sector New')

    def test_160_check_partner_id_calendar_event_as_client_of_task(self):
        self.task_1.request_reservation()
        calendar_event = self.task_1.get_calendar_event()
        self.assertEqual(
            calendar_event.client_id.id,
            self.partner_1.id
        )

    def test_170_update_task_event_clone_partner_ids_with_employee_ids(self):
        self.task_1.write({
            'employee_ids': [(6, 0, [self.employee_1.id])],
        })
        self.task_1.request_reservation()
        calendar_event_task = self.task_1.get_calendar_event()
        user = self.env['res.users']\
            .browse(self.task_1.employee_ids[0].user_id.id)
        self.assertEqual(user.partner_id,
                         calendar_event_task.partner_ids[0])
