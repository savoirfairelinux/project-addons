# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields
from .common import TestCalendarEventCommon
from odoo.exceptions import ValidationError


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
            'floor': '1',
        })
        self.vals = {
            'name': 'Calendar Event onchange method execution',
            'room_id': self.pre_room_id.id,
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'recurrent_state': 'No',
            'recurrence_type': 'datetype',
            'partner_ids': [(6, 0, [self.partner_1.id, self.partner_2.id])],
            'client_id': self.partner_1.id,
        }
        self.calendar_event = self.Calendar.create(self.vals)

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
        self.calendar_event._compute_calculate_recurrent()
        self.assertEqual(self.calendar_event.recurrent_state, 'No')

        self.recurrency = True
        self.calendar_event._compute_calculate_recurrent()
        self.calendar_event.recurrent_state = 'Yes'
        self.assertEqual(self.calendar_event.recurrent_state, 'Yes')

    def test_030_calculate_recurrence_type(self):
        self.end_type = 'end_date'
        self.recurrency = True
        self.calendar_event.recurrence_type = 'datetype'
        self.calendar_event._compute_calculate_recurrence_type()
        self.assertEqual(self.calendar_event.recurrence_type, 'datetype')

        self.recurrency = True
        self.end_type = 'others'
        self.calendar_event.recurrence_type = 'Iternationtype'
        self.calendar_event._compute_calculate_recurrence_type()
        self.assertEqual(self.calendar_event.recurrence_type, 'Iternationtype')

    def test_040_get_client_id_partner_ids_names(self):
        self.assertEqual(
            self.calendar_event.client_id_partner_ids_names,
            'Partner 1, Partner 2')

    def test_050_check_room_double_book(self):
        self.pre_room_id.allow_double_book = False
        with self.assertRaises(ValidationError):
            self.calendar_event1 = self.Calendar.create({
                'name': 'Calendar Event Test booking 1',
                'room_id': self.pre_room_id.id,
                'start': fields.Datetime.to_string(datetime.today()),
                'stop': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
                'recurrent_state': 'No',
            })
        self.pre_room_id.allow_double_book = True
        self.calendar_event2 = self.Calendar.create({
            'name': 'Calendar Event Test booking 2',
            'room_id': self.pre_room_id.id,
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'recurrent_state': 'No',
        })

    def test_060_check_equipment_double_book(self):
        self.instrument_1.allow_double_book = False
        self.calendar_event3 = self.Calendar.create({
            'name': 'Calendar Event Test booking 3',
            'equipment_ids': [(6, 0, [self.instrument_1.id,
                                      self.instrument_2.id])],
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'recurrent_state': 'No',
        })

        self.calendar_event4 = self.Calendar.create({
            'name': 'Calendar Event Test booking 4',
            'equipment_ids': [(6, 0, [self.instrument_2.id])],
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'recurrent_state': 'No',
        })
        with self.assertRaises(ValidationError):
            self.calendar_event5 = self.Calendar.create({
                'name': 'Calendar Event Test booking 5',
                'equipment_ids': [(6, 0, [self.instrument_1.id,
                                          self.instrument_2.id
                                          ])],
                'start': fields.Datetime.to_string(datetime.today()),
                'stop': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
                'recurrent_state': 'No',
            })

    def test_070_with_is_not_task_event_client_becomes_a_participant(
            self):
        vals = {
            'name': 'Calendar Event onchange method execution',
            'room_id': self.pre_room_id.id,
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'recurrent_state': 'No',
            'recurrence_type': 'datetype',
            'partner_ids': [(6, 0, [self.partner_1.id, self.partner_2.id])],
            'client_id': self.partner_3.id,
        }
        calendar_event_new = self.Calendar.create(vals)
        self.assertIn(self.partner_3, calendar_event_new.partner_ids)

    def test_080_write_add_client_to_participants(self):
        self.calendar_event.write({'client_id': self.partner_3.id})
        self.assertIn(self.partner_3, self.calendar_event.partner_ids)

    def test_090_cannot_remove_client_from_participants(self):
        partners_before_delete_client_id = self.calendar_event.partner_ids.ids
        self.calendar_event.write(
            {'partner_ids': [(6, 0, [self.partner_2.id])]})
        self.assertEqual(
            self.calendar_event.partner_ids.ids,
            partners_before_delete_client_id)

    def test_100_change_client_with_no_participants_puts_new_participant(
            self):
        partner_4 = self.Partners.create({
            'name': 'Partner 4',
        })
        self.calendar_event.write(
            {'client_id': partner_4.id, 'partner_ids': [(6, 0, [])]})
        self.assertEqual(self.calendar_event.partner_ids.ids, [partner_4.id])

    def test_110_floor(self):
        self.calendar_event1 = self.Calendar.create({
            'name': 'Calendar Event Test floor',
            'room_id': self.post_room_id.id,
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'recurrent_state': 'No',
        })
        self.assertEqual(
            self.post_room_id.floor,
            self.calendar_event1.room_floor
        )

    def test_120_recurrency_inverval_must_be_greater_than_0(
            self):
        with self.assertRaises(ValidationError):
            self.calendar_event.write({
                'rrule_type': 'daily',
                'recurrency': True,
                'interval': 0,
                'count': 2
            })

    def test_130_recurrency_count_must_be_greater_than_0(self):
        with self.assertRaises(ValidationError):
            self.calendar_event.write(
                {'rrule_type': 'daily', 'recurrency': True, 'count': 0})
