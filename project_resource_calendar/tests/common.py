# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestCalendarEventCommon(common.TransactionCase):

    def setUp(self):
        super(TestCalendarEventCommon, self).setUp()

        self.Rooms = self.env['resource.calendar.room']
        self.Instruments = self.env['resource.calendar.instrument']
        self.WeeklyReportWizards = self.env['weekly.report.wizard']
        self.Partners = self.env['res.partner']

        self.room_1 = self.Rooms.create({
            'name': 'Test Room 1',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.room_2 = self.Rooms.create({
            'name': 'Test Room 2',
            'resource_type': 'room',
            'allow_double_book': True,
            'is_bookable': False,
        })
        self.instrument_1 = self.Instruments.create({
            'name': 'Test Instrument 1',
            'resource_type': 'material',
            'room_id': self.room_1.id,
            'allow_double_book': True,
        })
        self.instrument_2 = self.Instruments.create({
            'name': 'Test Instrument 2',
            'resource_type': 'material',
            'room_id': self.room_1.id,
            'allow_double_book': True,
        })
        self.instrument_3 = self.Instruments.create({
            'name': 'Test Instrument 3',
            'resource_type': 'material',
            'room_id': self.room_1.id,
            'allow_double_book': True,
            'is_bookable': False,
        })
        self.weekly_report_wizard_common = self.WeeklyReportWizards.create({
            'room_id': self.room_1.id,
            'recurrency': True,
            'state': 'open',
        })
        self.partner_1 = self.Partners.create({
            'name': 'Partner 1',
        })

        self.partner_2 = self.Partners.create({
            'name': 'Partner 2',
        })
        self.partner_3 = self.Partners.create({
            'name': 'Partner 3',
        })
