# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common
import datetime


class TestWeeklyReportWizard(common.TransactionCase):

    def setUp(self):
        super(TestWeeklyReportWizard, self).setUp()
        self.Rooms = self.env['resource.calendar.room']
        self.WeeklyReportWizard = self.env['weekly.report.wizard']
        self.EMPLOYEE_BASE = self.env.ref(
            'base.group_user')
        self.EMPLOYEE_GROUP = self.env.ref(
            'project_resource_calendar.group_resource_calendar_user')
        self.RESOURCE_CALENDAR_MANAGER = self.env.ref(
            'project_resource_calendar.group_resource_calendar_manager')
        self.RESOURCE_CALENDAR_EDITOR = self.env.ref(
            'project_resource_calendar.group_resource_calendar_editor')
        self.room_1 = self.Rooms.create({
            'name': 'Test Room 1',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.weekly_report_wizard_1 = self.WeeklyReportWizard.create({
            'room_id': self.room_1.id,
            'recurrency': True,
            'state': 'open',
        })
        self.Users = self.env['res.users']
        self.Employees = self.env['hr.employee']
        self.user_base = self.Users.create({
            'name': 'Base User',
            'login': 'base@test.com',
            'groups_id': [(6, 0, [self.EMPLOYEE_BASE.id])]
        })
        self.user_guest = self.Users.create({
            'name': 'Guest',
            'login': 'guest@test.com',
            'groups_id': [(6, 0, [self.EMPLOYEE_GROUP.id])]
        })
        self.user_editor = self.Users.create({
            'name': 'Editor',
            'login': 'editor@test.com',
            'groups_id': [(6, 0, [self.RESOURCE_CALENDAR_EDITOR.id])]
        })
        self.user_manager = self.Users.create({
            'name': 'Manager',
            'login': 'manager@test.com',
            'groups_id': [(6, 0, [self.RESOURCE_CALENDAR_MANAGER.id])]
        })
        self.employee_base = self.Employees.create({
            'name': 'Base User',
            'work_email': 'base@test.com',
            'user_id': self.user_base.id,
        })
        self.employee_guest = self.Employees.create({
            'name': 'Guest',
            'work_email': 'guest@test.com',
            'user_id': self.user_guest.id,
        })
        self.employee_editor = self.Employees.create({
            'name': 'Editor',
            'work_email': 'editor@test.com',
            'user_id': self.user_editor.id,
        })
        self.employee_manager = self.Employees.create({
            'name': 'Manager',
            'work_email': 'manager@test.com',
            'user_id': self.user_manager.id,
        })

    def test_010_get_current_monday(self):
        monday = self.weekly_report_wizard_1._get_current_monday().weekday()
        self.assertEqual(monday, 0)

    def test_020_get_current_friday(self):
        friday = self.weekly_report_wizard_1._get_current_friday().weekday()
        self.assertEqual(friday, 4)

    def test_030_default_date_start(self):
        start_weekday = datetime.datetime.strptime(
            self.weekly_report_wizard_1.date_start,
            '%Y-%m-%d'
        ).weekday()
        self.assertEqual(start_weekday, 0)

    def test_040_default_date_end(self):
        end_weekday = datetime.datetime.strptime(
            self.weekly_report_wizard_1.date_end,
            '%Y-%m-%d'
        ).weekday()
        self.assertEqual(end_weekday, 4)

    def test_050_get_report(self):
        report = self.weekly_report_wizard_1.get_report()
        self.assertEqual(
            report['data']['form']['room_id'],
            self.room_1.id
        )
        self.assertEqual(
            report['data']['form']['date_start'],
            self.weekly_report_wizard_1.date_start
        )
        self.assertEqual(
            report['data']['form']['date_end'],
            self.weekly_report_wizard_1.date_end
        )
        self.assertEqual(
            report['data']['form']['recurrency'],
            self.weekly_report_wizard_1.recurrency
        )
        self.assertEqual(
            report['data']['form']['state'],
            self.weekly_report_wizard_1.state
        )

    def has_access_to_menu(self, user_id, menu_ref):
        user = self.env['res.users'].browse(user_id)
        for group in user.groups_id:
            for m in group.menu_access:
                if m.name == self.env.ref(menu_ref).name:
                    return True
        return False

    def test_060_base_user_cannot_get_weekly_report_menu(self):
        self.assertFalse(self.has_access_to_menu(
            self.user_base.id,
            'calendar_event_report.menu_event_reports'))

    def test_070_guest_user_cannot_get_weekly_report_menu(self):
        self.assertFalse(self.has_access_to_menu(
            self.user_guest.id,
            'calendar_event_report.menu_event_reports'))

    def test_080_editor_user_cannot_get_weekly_report_menu(self):
        self.assertFalse(self.has_access_to_menu(
            self.user_editor.id,
            'calendar_event_report.menu_event_reports'))

    def test_090_manager_user_can_get_weekly_report_menu(self):
        self.assertTrue(self.has_access_to_menu(
            self.user_manager.id,
            'calendar_event_report.menu_event_reports'))
