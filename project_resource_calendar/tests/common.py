# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common


class TestCalendarEventCommon(common.TransactionCase):

    def setUp(self):
        super(TestCalendarEventCommon, self).setUp()

        # Usefull models
        self.Calendar = self.env['calendar.event']
        self.Rooms = self.env['resource.calendar.room']
        self.Instruments = self.env['resource.calendar.instrument']

        self.room_1 = self.Rooms.create({
            'name': 'Test Room 1',
        })
        self.instrument_1 = self.Instruments.create({
            'name': 'Test Intrument 1',
        })
