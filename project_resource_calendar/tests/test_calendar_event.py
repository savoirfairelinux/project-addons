# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import datetime, timedelta

from odoo import fields
from odoo.addons.project_resource_calendar.tests.common import TestCalendarEventCommon


class TestCalendarEvent(TestCalendarEventCommon):

    def setUp(self):
        super(TestCalendarEvent, self).setUp()
        self.Calendar = self.env['calendar.event']

        self.pre_room_id = self.Rooms.create({
            'name': 'Test Room id before onchange method execution',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.post_room_id = self.Rooms.create({
            'name': 'Test Room id after onchange method execution',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.calendar_event = self.Calendar.create({
            'name': 'Calendar Event onchange method execution',
            'room_id': self.pre_room_id.id,
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'recurrent_state': 'No',
            'recurrence_type': 'datetype',
        })

    def test_010_onchange_room_id(self):
        self.assertEqual(self.calendar_event.name,
                         'Calendar Event onchange method execution')
        self.assertEqual(self.pre_room_id.name,
                         'Test Room id before onchange method execution')
        self.assertEqual(self.calendar_event.room_id.name,
                         'Test Room id before onchange method execution')
        self.calendar_event.room_id = self.post_room_id
        self.calendar_event._onchange_room_id()
        self.assertEqual(self.calendar_event.room_id.name,
                         'Test Room id after onchange method execution')

    def test_020_calculate_recurrent(self):
        self.recurrency = False
        self.calendar_event._calculate_recurrent()
        self.assertEqual(self.calendar_event.recurrent_state, 'No')

        self.recurrency = True
        self.calendar_event._calculate_recurrent()
        self.calendar_event.recurrent_state = 'Yes'
        self.assertEqual(self.calendar_event.recurrent_state, 'Yes')

    def test_030_calculate_recurrence_type(self):
        self.end_type = 'end_date'
        self.recurrency = True
        self.calendar_event.recurrence_type = 'datetype'
        self.calendar_event._calculate_recurrence_type()
        self.assertEqual(self.calendar_event.recurrence_type, 'datetype')

        self.recurrency = True
        self.end_type = 'others'
        self.calendar_event.recurrence_type = 'Iternationtype'
        self.calendar_event._calculate_recurrence_type()
        self.assertEqual(self.calendar_event.recurrence_type, 'Iternationtype')
