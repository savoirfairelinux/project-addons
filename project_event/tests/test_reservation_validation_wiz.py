# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common
from datetime import datetime, timedelta
from odoo import fields


class TestDoubleBookingValidationWizard(common.TransactionCase):

    def setUp(self):
        super(TestDoubleBookingValidationWizard, self).setUp()
        self.Calendar = self.env['calendar.event']
        self.ProjectTask = self.env['project.task']
        self.ValidationWizard = self.env['doublebooking.validation.wiz']
        self.Rooms = self.env['resource.calendar.room']

        self.room_1 = self.Rooms.create({
            'name': 'Test Room 1',
            'resource_type': 'room',
            'allow_double_book': True,
        })

        vals_calendar = {
            'name': 'Calendar Event 1',
            'room_id': self.room_1.id,
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4))
        }
        self.calendar_event = self.Calendar.create(vals_calendar)

        vals_task = {
            'name': 'Task Event 1',
            'room_id': self.room_1.id,
            'activity_task_type': 'task',
            'task_state': 'requested',
            'parent_id': None,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4))
        }
        self.project_task = self.ProjectTask.create(vals_task)

        self.new_starting_date = fields.Datetime.to_string(
            datetime.strptime(self.project_task.date_start,
                              '%Y-%m-%d %H:%M:%S') +
            timedelta(hours=1))
        self.new_ending_date = fields.Datetime.to_string(
            datetime.strptime(self.project_task.date_end,
                              '%Y-%m-%d %H:%M:%S') +
            timedelta(hours=1))

    def test_010_create_validation_wizard_calendar_event(self):
        validationWizardCalendar = self.ValidationWizard.create(
            {
                'event_id': self.calendar_event.id,
                'message': 'Warning double booking',
                'start_date': fields.Datetime.to_string(
                    datetime.strptime(self.calendar_event.start,
                                      '%Y-%m-%d %H:%M:%S') +
                    timedelta(hours=1)),
                'end_date': fields.Datetime.to_string(
                    datetime.strptime(self.calendar_event.stop,
                                      '%Y-%m-%d %H:%M:%S') +
                    timedelta(hours=1)),
                'r_start_date': self.calendar_event.start,
                'r_end_date': self.calendar_event.stop,
            })
        self.assertNotEqual(validationWizardCalendar.id, False)

    def test_020_create_validation_wizard_project_event_task(self):
        validationWizardTask = self.ValidationWizard.create(
            {
                'task_id': self.project_task.id,
                'message': 'Warning double booking',
                'start_date': self.new_starting_date,
                'end_date': self.new_ending_date,
                'r_start_date': self.project_task.date_start,
                'r_end_date': self.project_task.date_end,
            })
        self.assertNotEqual(validationWizardTask.id, False)

    def test_030_check_task_calendar_overlap_confirm_update(self):
        self.assertEqual(len(self.project_task.
                         get_double_booked_resources(self.new_starting_date,
                                                     self.new_ending_date)), 1)
        validationWizardTask = self.ValidationWizard.create(
            {
                'task_id': self.project_task.id,
                'message': 'Warning double booking',
                'start_date': self.new_starting_date,
                'end_date': self.new_ending_date,
                'r_start_date': self.project_task.date_start,
                'r_end_date': self.project_task.date_end,
            })
        validationWizardTask.confirm_update()
        self.assertEqual(self.project_task.date_start, self.new_starting_date)
        self.assertEqual(self.project_task.date_end, self.new_ending_date)

    def test_040_check_task_calendar_overlap_confirm_cancel(self):
        old_starting_date = self.project_task.date_start
        old_ending_date = self.project_task.date_end
        self.assertEqual(len(self.project_task.
                         get_double_booked_resources(self.new_starting_date,
                                                     self.new_ending_date)), 1)
        validationWizardTask = self.ValidationWizard.create(
            {
                'task_id': self.project_task.id,
                'message': 'Warning double booking',
                'start_date': self.new_starting_date,
                'end_date': self.new_ending_date,
                'r_start_date': self.project_task.date_start,
                'r_end_date': self.project_task.date_end,
            })
        validationWizardTask.confirm_cancel()
        self.assertEqual(self.project_task.date_start, old_starting_date)
        self.assertEqual(self.project_task.date_end, old_ending_date)
        self.assertNotEqual(self.project_task.date_start,
                            self.new_starting_date)
        self.assertNotEqual(self.project_task.date_end, self.new_ending_date)
