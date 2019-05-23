# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common
from datetime import datetime, timedelta


class TestDoubleBookingValidationWizard(common.TransactionCase):

    def setUp(self):
        super(TestDoubleBookingValidationWizard, self).setUp()
        self.Calendar = self.env['calendar.event']
        self.ProjectTask = self.env['project.task']
        self.ReservationValidationWizard = \
            self.env['doublebooking.validation.wiz']

        self.vals_calendar = {
            'name': 'Calendar Event 1',
            'start': datetime.today(),
            'stop': datetime.today() + timedelta(hours=4),
        }
        self.calendar_event = self.Calendar.create(self.vals_calendar)


        import pdb
        pdb.set_trace()

        self.vals_task = {
            'name': 'Task Event 1',
            'activity_task_type': 'task',
            'parent_id': None,
            'date_start': datetime.today(),
            'date_end': datetime.today() + timedelta(hours=4),
        }
        self.project_task = self.ProjectTask.create(self.vals_task)


    def test_010_create_validation_wizard_calendar_event(self):
        self.ReservationValidationWizard_calendar = \
            self.ReservationValidationWizard.create(
            {
                'event_id': self.calendar_event.id,
                'message': 'Warning double booking',
                'start_date': self.calendar_event.start + timedelta(hours=4),
                'end_date': self.calendar_event.stop + timedelta(hours=4),
                'r_start_date': self.calendar_event.start,
                'r_end_date': self.calendar_event.stop,
            })

        self.assertEqual(self.ReservationValidationWizard_calendar.id, True)

    def test_020_create_validation_wizard_project_event_task(self):
        self.ReservationValidationWizard_calendar = \
            self.ReservationValidationWizard.create(
            {
                'task_id': self.project_task.id,
                'message': 'Warning double booking',
                'start_date': self.project_task.date_start +
                              timedelta(hours=4),
                'end_date': self.project_task.date_end + timedelta(hours=4),
                'r_start_date': self.project_task.date_start,
                'r_end_date': self.project_task.date_end,
            })

        self.assertEqual(self.ReservationValidationWizard_task.id, True)
