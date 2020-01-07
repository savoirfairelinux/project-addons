# © 2019 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCalendarEventCommon
from odoo import exceptions, fields
from datetime import datetime, timedelta


class TestSecurity(TestCalendarEventCommon):

    def setUp(self):
        super(TestSecurity, self).setUp()
        self.EMPLOYEE_BASE = self.env.ref(
            'base.group_user')
        self.EMPLOYEE_GROUP = self.env.ref(
            'project_resource_calendar.group_resource_calendar_user')
        self.RESOURCE_CALENDAR_MANAGER = self.env.ref(
            'project_resource_calendar.group_resource_calendar_manager')
        self.RESOURCE_CALENDAR_EDITOR = self.env.ref(
            'project_resource_calendar.group_resource_calendar_editor')
        self.Users = self.env['res.users']
        self.Tag_categories = self.env['hr.employee.category']
        self.Employees = self.env['hr.employee']
        self.Events = self.env['calendar.event']
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
        self.tag_base = self.Tag_categories.create({'name': 'base'})
        self.tag_guest = self.Tag_categories.create({'name': 'guest'})
        self.tag_editor = self.Tag_categories.create({'name': 'editor'})
        self.tag_manager = self.Tag_categories.create({'name': 'manager'})
        self.employee_base = self.Employees.create({
            'name': 'Base User',
            'work_email': 'base@test.com',
            'user_id': self.user_base.id,
            'category_ids': [(6, 0, [self.tag_base.id])]
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
        self.room_calendar_event_user = self.Rooms.create({
            'name': 'Test Room Tag Calendar Event User',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.add_room_to_group(
            self.EMPLOYEE_GROUP,
            self.room_calendar_event_user)
        self.room_base_user = self.Rooms.create({
            'name': 'Test Room Tag Base User',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.add_room_to_group(self.EMPLOYEE_BASE, self.room_base_user)
        self.room_editor_user = self.Rooms.create({
            'name': 'Test Room Tag Editor User',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.user_editor.partner_id.write({'email': 'editor@test.com'})
        self.add_room_to_group(
            self.RESOURCE_CALENDAR_EDITOR,
            self.room_editor_user)

    @staticmethod
    def add_room_to_group(group, room):
        group.write({'room_ids': [(6, 0, [room.id])]})

    def get_user_groups(self, user_id):
        user = self.env['res.users'].browse(user_id)
        return user.groups_id

    def get_group_access_rules(self, group_id):
        group = self.env['res.groups'].browse(group_id)
        return group.model_access

    @staticmethod
    def has_read_permission(access_rule):
        return access_rule.perm_read

    def cannot_create_room(self, user_id, room_name):
        with self.assertRaises(exceptions.AccessError):
            self.env['resource.calendar.room'].sudo(
                user_id).create({'name': room_name})

    def test_010_base_user_can_not_create_rooms(self):
        self.cannot_create_room(self.user_base.id, 'Room base')

    def test_020_guest_user_can_not_create_rooms(self):
        self.cannot_create_room(self.user_guest.id, 'Room guest')

    def test_030_editor_user_can_not_create_rooms(self):
        self.cannot_create_room(self.user_editor.id, 'Room editor')

    def test_040_manager_user_can_create_rooms(self):
        room_manager = self.env['resource.calendar.room'].sudo(
            self.user_manager).create({'name': 'Manager Room'})
        self.assertIsInstance(
            room_manager,
            type(self.Rooms))

    def test_050_base_user_cannot_read_events_where_he_is_not_participant(
            self):
        self.assertEqual(
            len(self.Events.sudo(self.user_base.id).search([])),
            0)

    def create_event(
            self,
            name,
            partner_ids=None,
            room_id=None,
            user_id=1,
            equipment_ids=None):
        if not partner_ids:
            partner_ids = []
        if not equipment_ids:
            equipment_ids = []
        return self.Events.sudo(user_id).create({
            'name': name,
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'recurrent_state': 'No',
            'recurrence_type': 'datetype',
            'partner_ids': [(6, 0, partner_ids)],
            'room_id': room_id,
            'equipment_ids': [(6, 0, equipment_ids)],
        })

    def user_can_read_event(
            self,
            name,
            user_id,
            partner_ids=None,
            room_id=None):
        if not partner_ids:
            partner_ids = []
        calendar_event_user_event = self.create_event(
            name,
            partner_ids,
            room_id,)
        calendar_user_read_events =\
            self.Events.sudo(user_id).search([])
        self.assertEqual(
            len(calendar_user_read_events),
            1)
        self.assertEqual(
            calendar_user_read_events.id,
            calendar_event_user_event.id)

    def test_060_base_user_can_read_calendar_events_where_he_is_participant(
            self):
        self.user_can_read_event(
            'Calendar Event where base user is participant',
            self.user_base.id,
            [self.user_base.partner_id.id])

    def test_070_guest_user_can_read_calendar_events_where_he_is_participant(
            self):
        self.user_can_read_event(
            'Calendar Event where guest user is participant',
            self.user_guest.id,
            [self.user_guest.partner_id.id])

    def test_080_guest_user_can_read_calendar_events_with_room_with_his_group(
            self):
        self.user_can_read_event(
            'Calendar Event with room guest user tag',
            self.user_guest.id,
            [],
            self.room_calendar_event_user.id)

    def test_081_editor_user_can_read_calendar_events_where_he_is_participant(
            self):
        self.create_event(
            'Editor is participant', [self.user_editor.partner_id.id])
        events_participant = self.Events.search(
            [('partner_ids', 'in', self.user_editor.partner_id.id)])
        for event in events_participant:
            self.assertEqual(
                self.Events.sudo(self.user_editor.id).browse(event.id),
                event)

    def test_082_editor_user_can_read_calendar_events_with_room_with_his_group(
            self):
        self.create_event(
            'Editor is participant', [], self.room_editor_user.id)
        events_room = self.Events.search(
            [(
                'room_id.group_ids',
                'in',
                self.user_editor.groups_id.ids)])
        for event in events_room:
            self.assertEqual(
                self.Events.sudo(self.user_editor.id).browse(event.id),
                event)

    def test_083_manager_user_can_read_calendar_events(self):
        for event in self.Events.search([]):
            self.assertEqual(
                self.Events.sudo(self.user_manager.id).browse(event.id),
                event
            )

    def test_090_base_user_cannot_read_calendar_events_with_room_with_his_grp(
            self):
        self.create_event(
            'Calendar Event with room base user tag',
            [],
            self.room_base_user.id)
        self.assertEqual(
            len(self.Events.sudo(self.user_base.id).search([])),
            0)

    def user_cannot_write_room(self, user_id, room_id):
        room = self.Rooms.browse(room_id)
        with self.assertRaises(exceptions.AccessError):
            room.sudo(user_id).write({'name': 'New Name Fail!'})

    def test_130_base_user_cannot_write_rooms(self):
        self.user_cannot_write_room(
            self.user_base.id,
            self.room_base_user.id)

    def test_140_guest_user_cannot_write_rooms(self):
        self.user_cannot_write_room(
            self.user_guest.id,
            self.room_calendar_event_user.id)

    def test_150_editor_user_cannot_write_rooms(self):
        self.user_cannot_write_room(
            self.user_editor.id,
            self.room_editor_user.id)

    def test_160_manager_user_can_write_rooms(self):
        room = self.Rooms.browse(self.room_editor_user.id)
        room.sudo(self.user_manager.id).write({'name': 'New Name 160'})
        self.assertEqual(room.name, 'New Name 160')

    def test_170_base_user_cannot_read_rooms(self):
        with self.assertRaises(exceptions.AccessError):
            self.Rooms.sudo(self.user_base.id).search([])

    def user_can_read_rooms_with_his_tag(self, user):
        for room in self.Rooms.sudo(user.id).search([]):
            self.assertIn(
                room.group_ids, user.groups_id)

    def test_180_guest_user_can_read_rooms_with_same_tag(self):
        self.user_can_read_rooms_with_his_tag(self.user_guest)

    def test_190_editor_user_can_read_rooms_with_same_tag(self):
        self.user_can_read_rooms_with_his_tag(self.user_editor)

    def test_200_manager_user_can_read_rooms(self):
        self.assertEqual(
            self.Rooms.search([]),
            self.Rooms.sudo(self.user_manager.id).search([]))

    def user_cannot_delete_rooms(self, user_id):
        with self.assertRaises(exceptions.AccessError):
            self.Rooms.sudo(user_id).search([]).unlink()

    def test_210_base_user_cannot_delete_rooms(self):
        self.user_cannot_delete_rooms(self.user_base.id)

    def test_220_guest_user_cannot_delete_rooms(self):
        self.user_cannot_delete_rooms(self.user_guest.id)

    def test_230_editor_user_cannot_delete_rooms(self):
        self.user_cannot_delete_rooms(self.user_editor.id)

    def test_230_manager_user_can_delete_rooms(self):
        room = self.Rooms.create({'name': 'Will be deleted'})
        self.assertTrue(
            room.sudo(self.user_manager.id).unlink())

    def user_cannot_create_instrument(self, user_id):
        with self.assertRaises(exceptions.AccessError):
            self.Instruments.sudo(user_id).create({'name': 'New Ins.'})

    def test_120_base_user_cannot_create_instruments(self):
        self.user_cannot_create_instrument(self.user_base.id)

    def test_240_guest_user_cannot_create_instruments(self):
        self.user_cannot_create_instrument(self.user_guest.id)

    def test_250_editor_user_cannot_create_instruments(self):
        self.user_cannot_create_instrument(self.user_editor.id)

    def test_260_manager_user_can_create_instruments(self):
        self.assertEqual(
            self.Instruments.sudo(self.user_manager.id).create(
                {'name': 'New 260'}).name,
            'New 260')

    def test_270_base_user_cannot_read_instruments(self):
        with self.assertRaises(exceptions.AccessError):
            self.Instruments.sudo(self.user_base.id).search([])

    # TO DO: Validate Spec and write these:
    # def test_280_guest_user_can_
    # read_instruments_from_rooms_with_his_tag(self):
    # def
    # test_290_editor_user_can_read_instruments_from
    # _rooms_with_his_tag(self):

    def test_300_manager_user_can_read_instruments(self):
        self.assertEqual(
            self.Instruments.search([]),
            self.Instruments.sudo(self.user_manager.id).search([]))

    def user_cannot_write_instrument(self, user_id):
        with self.assertRaises(exceptions.AccessError):
            self.instrument_1.sudo(
                user_id).write({'name': 'New Name Fail!'})

    def test_310_base_user_cannot_write_instruments(self):
        self.user_cannot_write_instrument(self.user_base.id)

    def test_320_guest_user_cannot_write_instruments(self):
        self.user_cannot_write_instrument(self.user_guest.id)

    def test_330_editor_user_cannot_write_instruments(self):
        self.user_cannot_write_instrument(self.user_editor.id)

    def test_340_manager_user_can_write_instruments(self):
        self.assertEqual(
            self.instrument_1.sudo(self.user_manager.id).write(
                {'name': 'New Name 340'}),
            True)
        self.instrument_1.write({'name': 'Test Instrument 1'})

    def user_cannot_delete_instruments(self, user_id):
        with self.assertRaises(exceptions.AccessError):
            self.Instruments.sudo(user_id).search([]).unlink()

    def test_350_base_user_cannot_delete_instruments(self):
        self.user_cannot_delete_instruments(self.user_base.id)

    def test_360_guest_user_cannot_delete_instruments(self):
        self.user_cannot_delete_instruments(self.user_guest.id)

    def test_370_editor_user_cannot_delete_instruments(self):
        self.user_cannot_delete_instruments(self.user_editor.id)

    def test_380_manager_user_can_delete_instruments(self):
        instrument = self.Instruments.create({'name': 'Will be deleted'})
        self.assertTrue(
            instrument.sudo(self.user_manager.id).unlink())

    def user_cannot_write_events(self, partner_id, user_id):
        calendar_event = self.create_event(
            'Calendar Event where user is participant',
            [partner_id],
        )
        with self.assertRaises(exceptions.AccessError):
            calendar_event.sudo(
                user_id).write({})

    def test_100_base_user_cannot_write_events(self):
        self.user_cannot_write_events(
            self.user_base.partner_id.id,
            self.user_base.id)

    def test_110_guest_user_cannot_write_events_where_he_participates(self):
        self.user_cannot_write_events(
            self.user_guest.partner_id.id,
            self.user_guest.id)

    def test_390_editor_user_can_write_events_where_he_participates(self):
        calendar_event = self.create_event(
            'Calendar Event where editor user is participant',
            [self.user_editor.partner_id.id],
        )
        self.assertTrue(
            calendar_event.sudo(
                self.user_editor.id).write({}))

    def test_400_editor_user_can_write_events_with_room_with_his_group(self):
        calendar_event = self.create_event(
            'Calendar Event where editor user is participant',
            [],
            self.room_editor_user.id
        )
        self.assertTrue(
            calendar_event.sudo(
                self.user_editor.id).write({}))

    def test_410_manager_user_can_write_events(self):
        for event in self.Events.search([]):
            self.assertTrue(
                event.sudo(self.user_manager.id).write({})
            )

    def has_access_to_menu(self, user_id, menu_ref):
        user = self.env['res.users'].browse(user_id)
        for group in user.groups_id:
            for m in group.menu_access:
                if m.name == self.env.ref(menu_ref).name:
                    return True
        return False

    def test_960_base_user_cannot_get_weekly_report_menu(self):
        self.assertFalse(self.has_access_to_menu(
            self.user_base.id,
            'project_resource_calendar.menu_event_reports'))

    def test_970_guest_user_cannot_get_weekly_report_menu(self):
        self.assertFalse(self.has_access_to_menu(
            self.user_guest.id,
            'project_resource_calendar.menu_event_reports'))

    def test_980_editor_user_can_get_weekly_report_menu(self):
        self.assertTrue(self.has_access_to_menu(
            self.user_editor.id,
            'project_resource_calendar.menu_event_reports'))

    def test_420_base_user_cannot_delete_calendar_events(self):
        self.create_event(
            'Base user participant',
            [self.user_base.partner_id.id])
        with self.assertRaises(exceptions.AccessError):
            self.Events.sudo(self.user_base.id).search([]).unlink()

    def test_430_guest_user_cannot_delete_calendar_events(self):
        self.create_event(
            'Guest user participant',
            [self.user_guest.partner_id.id])
        with self.assertRaises(exceptions.AccessError):
            self.Events.sudo(
                self.user_guest.id).search([]).unlink()

    def test_440_editor_can_delete_calendar_events_where_he_is_participant(
            self):
        event = self.create_event(
            'Event editor is participant',
            [self.user_editor.partner_id.id]
        )
        self.assertTrue(
            event.sudo(self.user_manager.id).unlink())

    def test_450_editor_user_can_delete_calendar_events_with_room_with_his_grp(
            self):
        event = self.create_event(
            'Event room in editor tagst',
            [],
            self.room_editor_user.id
        )
        self.assertTrue(
            event.sudo(self.user_editor.id).unlink())

    def test_460_manager_user_can_delete_calendar_events(self):
        self.assertTrue(self.Events.sudo(
            self.user_manager).search([]).unlink())

    def test_470_base_user_cannot_create_calendar_events(self):
        with self.assertRaises(exceptions.AccessError):
            self.create_event('Not Created', [], None, self.user_base.id)

    def test_480_guest_user_cannot_create_calendar_events(self):
        with self.assertRaises(exceptions.AccessError):
            self.create_event('Not Created', [], None, self.user_guest.id)

    def test_490_editor_can_create_calendar_events_where_he_is_participant(
            self):
        event_editor = self.create_event(
            'Editor is Participant Event',
            [self.user_editor.partner_id.id],
            None,
            self.user_editor.id)
        self.assertIsInstance(
            event_editor,
            type(self.Events))

    def test_500_editor_user_can_create_calendar_events_with_room_with_his_grp(
            self):
        event_editor = self.create_event(
            'Editors Room Event',
            [],
            self.room_editor_user.id,
            self.user_editor.id)
        self.assertIsInstance(
            event_editor,
            type(self.Events))

    def test_510_editor_cant_cr_caev_without_room_w_his_tag_nor_participant(
            self):
        with self.assertRaises(exceptions.ValidationError):
            self.create_event(
                'Editors Room Event',
                [],
                None,
                self.user_editor.id)

    def test_520_manager_user_can_create_calendar_events(self):
        self.user_manager.partner_id.write({'email': 'manager@test.comx'})
        event_manager = self.create_event(
            'By Manager',
            [],
            None,
            self.user_manager.id)
        self.assertIsInstance(
            event_manager,
            type(self.Events))

    def test_530_cannot_book_not_bookable_room(self):
        with self.assertRaises(exceptions.ValidationError):
            self.create_event('Not bookable Room Event',
                              [],
                              self.room_2.id)

    def test_540_cannot_book_not_bookable_equipment(self):
        with self.assertRaises(exceptions.ValidationError):
            self.create_event('Not bookable Room Event',
                              [],
                              None,
                              1,
                              [self.instrument_3.id])
