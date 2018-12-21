# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from odoo.addons.project_resource_calendar.tests.common import TestCalendarEventCommon


class TestCalendarEvent(TestCalendarEventCommon):

    def setUp(self):
        super(TestCalendarEvent, self).setUp()

    def test_010_onchange_room_id(self):
        self.assertEqual(self.room_1.name, 'Test Room 1')
        self.assertEqual(self.instrument_1.name, 'Test Intrument 1')
