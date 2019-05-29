# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import datetime, timedelta
from odoo import exceptions
from odoo import fields
from .common import TestProjectEventCommon


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

    def test_060_workflow_task_actions(self):
        self.check_action_option(self.activity_1.child_ids)
        self.check_reservation_event_fields(self.activity_1.child_ids)
        self.check_action_request(self.activity_1.child_ids)
        self.check_action_accept(self.activity_1.child_ids)
        self.check_action_read(self.activity_1.child_ids)
        self.check_action_done(self.activity_1.child_ids)
        self.check_action_postpone(self.activity_1.child_ids)
        clone_event_ids = self.activity_1.child_ids.mapped(
            'reservation_event_id')
        self.check_action_cancel(self.activity_1.child_ids)
        self.check_clone_event_state(clone_event_ids, 'cancelled')

    def test_062_workflow_activity_actions(self):
        self.check_activity_action_option(self.activity_1)
        self.check_activity_action_accept(self.activity_1)
        self.check_activity_action_postpone(self.activity_1)
        self.check_activity_action_accept(self.activity_1)
        clone_event_ids = self.activity_1.child_ids.mapped(
            'reservation_event_id')
        self.check_action_cancel(self.activity_1)
        self.check_clone_event_state(clone_event_ids, 'cancelled')

    def test_065_action_return_option(self):
        self.do_action_request(self.activity_1.child_ids)
        self.check_action_return_option(self.activity_1.child_ids)

    def test_070_cancel_action(self):
        self.do_action_request(self.activity_1.child_ids)
        self.check_action_cancel(self.activity_1.child_ids)

    def check_action_option(self, task):
        self.do_action_option(task)
        self.assertEqual(task.task_state, 'option')
        self.check_reservation_event_state(task, 1, 'draft')

    def check_activity_action_option(self, activity):
        self.do_action_option(activity)
        self.assertEqual(activity.task_state, 'option')
        for task in activity.child_ids:
            self.check_reservation_event_state(task, 1, 'draft')
            self.check_reservation_event_fields(task)

    def do_action_option(self, task):
        res = task.action_option()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_reservation()

    def check_action_request(self, task):
        self.do_action_request(task)
        self.assertEqual(task.task_state, 'requested')
        self.check_reservation_event_state(task, 1, 'open')

    def do_action_request(self, task):
        res = task.action_request()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_request_reservation()

    def check_action_accept(self, task):
        self.do_action_accept(task)
        self.assertEqual(task.task_state, 'accepted')
        self.check_reservation_event_state(task, 1, 'open')

    def check_activity_action_accept(self, activity):
        self.do_action_accept(activity)
        self.assertEqual(activity.task_state, 'approved')
        for task in activity.child_ids:
            self.check_reservation_event_state(task, 1, 'open')

    def do_action_accept(self, task):
        res = task.action_accept()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_accept_reservation()

    def check_action_done(self, task):
        task.action_done()
        self.assertEqual(task.task_state, 'done')

    def check_action_read(self, task):
        task.action_read()
        self.assertEqual(task.task_state, 'read')

    def check_action_cancel(self, task):
        task.action_cancel()
        self.assertEqual(task.task_state, 'canceled')

    def check_action_postpone(self, task):
        task.action_postpone()
        self.assertEqual(task.task_state, 'postponed')
        self.check_reservation_event_state(task, 1, 'open')

    def check_activity_action_postpone(self, activity):
        activity.action_postpone()
        self.assertEqual(activity.task_state, 'postponed')
        for task in activity.child_ids:
            self.check_reservation_event_state(task, 1, 'open')

    def check_action_return_option(self, task):
        task.action_return_option()
        self.assertEqual(task.task_state, 'option')
        self.check_reservation_event_state(task, 1, 'draft')

    def check_activity_action_return_option(self, activity):
        activity.action_return_option()
        self.assertEqual(activity.task_state, 'option')
        for task in activity.child_ids:
            self.check_reservation_event_state(task, 1, 'draft')

    def check_reservation_event_state(self, task, number, state):
        reservation_event = task.info_calendar_event()
        self.assertEqual(len(reservation_event), number)
        self.assertEqual(reservation_event.state, state)

    def check_clone_event_state(self, event_ids, state):
        for event_id in event_ids:
            calendar_event = self.env['calendar.event'].browse(
                event_id)
            self.assertEqual(calendar_event.state, state)

    def check_reservation_event_fields(self, task):
        reservation_event = task.info_calendar_event()
        self.assertEqual(
            reservation_event.start,
            task.date_start)
        self.assertEqual(
            reservation_event.stop,
            task.date_end)
        self.assertEqual(
            reservation_event.name,
            task.complete_name)
        self.assertEqual(
            reservation_event.resource_type,
            task.resource_type)
        self.assertEqual(
            reservation_event.room_id,
            task.room_id)
        self.assertEqual(
            reservation_event.equipment_ids.ids,
            task.get_equipment_ids_inside())

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

    def test_180_check_clone_task_calendar_event(self):
        self.task_1.request_reservation()
        self.task_1.action_return_option()
        calendar_event = self.task_1.get_calendar_event()
        self.assertEqual(
            calendar_event.state,
            'draft'
        )

    def test_190_main_task_activity_calendar_event_clone_state(self):
        self.activity_1.request_reservation()
        for child in self.activity_1.child_ids:
            child.request_reservation()
        self.activity_1.action_return_option()
        for child in self.activity_1.child_ids:
            calendar_event = child.get_calendar_event()
            self.assertEqual(calendar_event.state, 'draft')

    def test_200_compute_actual_total_time(self):
        current_date = datetime.today()
        current_date_plus = current_date + timedelta(minutes=90)
        current_date_str = fields.Datetime.to_string(current_date)
        current_date_plus_str = fields.Datetime.to_string(
            current_date_plus)
        # Test case 1: Test for same actual start and end date
        task_vals_1 = {
            'name': 'Sample Task 1',
            'activity_task_type': 'task',
            'partner_id': self.project_1.partner_id.id,
            'room_id': self.room_1.id,
            'date_start': current_date_str,
            'date_end': current_date_plus_str,
            'real_date_start': current_date_str,
            'real_date_end': current_date_str,
        }
        task_1 = self.Tasks.create(task_vals_1)
        diff = task_1.actual_total_time
        self.assertEqual(diff, "00:00")

        # Test case 2: Test for different actual start and end date
        task_vals_2 = {
            'name': 'Sample Task 2',
            'activity_task_type': 'task',
            'partner_id': self.project_1.partner_id.id,
            'room_id': self.room_1.id,
            'date_start': current_date_str,
            'date_end': current_date_plus_str,
            'real_date_start': current_date_str,
            'real_date_end': current_date_plus_str,
        }
        task_2 = self.Tasks.create(task_vals_2)
        diff = task_2.actual_total_time
        self.assertEqual(diff, "01:30")

    def test_210_onchange_spectators(self):
        self.assertEqual(self.activity_3.spectators, '-')
        self.activity_3.spectators = '123'
        self.activity_3.onchange_spectators()
        self.assertEqual(self.activity_3.spectators, '123')
        self.activity_3.spectators = 'sfl'
        with self.assertRaises(exceptions.ValidationError):
            self.activity_3.onchange_spectators()
        self.activity_3.spectators = '999999999999'
        with self.assertRaises(exceptions.ValidationError):
            self.activity_3.onchange_spectators()

    def test_220_get_parent_project_id(self):
        self.task_2.parent_id = self.activity_2
        self.activity_2.project_id = self.project_2
        self.assertEqual(
            self.task_2.get_parent_project_id(),
            self.project_2.id
        )

    def test_230_is_type_task(self):
        self.assertTrue(self.task_1.is_type_task())

    def test_240_check_task_state(self):
        self.assertTrue(self.task_1.check_task_state('draft'))
        self.assertFalse(self.task_1.check_task_state('approved'))

    def test_250_duplicate_activity_duplicates_child_ids(self):
        self.task_1.write({'parent_id': self.activity_1.id})
        new_activity = self.activity_1.copy()
        self.assertEqual(
            len(self.activity_1.child_ids),
            len(new_activity.child_ids)
        )

    def test_260_is_hr_resource_booked(self):
        vals = {
            'name': 'Calendar Event Test HR Booking',
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'partner_ids': [(6, 0, [
                self.partner_1.id, self.partner_2.id])],
        }
        self.env['calendar.event'].create(vals)
        self.assertTrue(
            self.task_1.is_hr_resource_booked(self.partner_1.id)
        )
        self.assertTrue(
            self.task_1.is_hr_resource_booked(self.partner_2.id)
        )
        self.assertFalse(
            self.task_1.is_hr_resource_booked(self.partner_3.id)
        )
