# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from odoo.addons.project_event.tests.common import TestCalendarEventCommon


class TestCalendarEvent(TestCalendarEventCommon):

    def setUp(self):
        super(TestCalendarEvent, self).setUp()
        self.Calendar = self.env['calendar.event']
        self.equipment_ids = self.env['resource.calendar.instrument']

        self.calendar_1 = self.Calendar.create({
            'name': 'Test Calendar 1',
            'room_id': self.room_1.id,
            'resource_ids': self.resource_1.id,
            'equipment_ids': self.equipment_1.id,
        })

    def test_010_onchange_room_id(self):
        self.assertEqual(self.calendar_1.room_id.name, 'Test Room 1')
        self.assertEqual(self.calendar_1.equipment_ids.name, 'Test Intrument 1')
