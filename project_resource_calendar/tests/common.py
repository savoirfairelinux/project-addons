# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common


class TestCalendarEventCommon(common.TransactionCase):

    def setUp(self):
        super(TestCalendarEventCommon, self).setUp()

        self.Rooms = self.env['resource.calendar.room']
        self.Instruments = self.env['resource.calendar.instrument']
        self.WeeklyReportWizards = self.env['weekly.report.wizard']

        self.room_1 = self.Rooms.create({
            'name': 'Test Room 1',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.instrument_1 = self.Instruments.create({
            'name': 'Test Instrument 1',
            'resource_type': 'material',
            'room_id': self.room_1.id,
            'allow_double_book': True,
        })
        self.weekly_report_wizard_common = self.WeeklyReportWizards.create({
                'room_id': self.room_1.id,
                'recurrency': True,
                'state': 'open',
            })
