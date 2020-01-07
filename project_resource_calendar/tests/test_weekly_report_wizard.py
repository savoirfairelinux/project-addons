# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCalendarEventCommon
import datetime


class TestWeeklyReportWizard(TestCalendarEventCommon):

    def setUp(self):
        super(TestWeeklyReportWizard, self).setUp()
        self.WeeklyReportWizard = self.env['weekly.report.wizard']
        self.weekly_report_wizard_1 = self.WeeklyReportWizard.create({
            'room_id': self.room_1.id,
            'recurrency': True,
            'state': 'open',
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
