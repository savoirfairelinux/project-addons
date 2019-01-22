# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.addons.project_resource_calendar.tests.common import TestCalendarEventCommon
from odoo import exceptions

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
        self.user_base = self.Users.create({
                'name': 'Base User',
                'login': 'base@test.com',
                'groups_id': [(6, 0,[self.EMPLOYEE_BASE.id] )]
            })
        self.user_guest = self.Users.create({
                'name': 'Guest',
                'login': 'guest@test.com',
                'groups_id': [(6, 0,[self.EMPLOYEE_GROUP.id] )]
            })
        self.user_editor = self.Users.create({
                'name': 'Editor',
                'login': 'editor@test.com',
                'groups_id': [(6, 0,[self.RESOURCE_CALENDAR_EDITOR.id] )]
            })
        self.user_manager = self.Users.create({
                'name': 'Manager',
                'login': 'manager@test.com',
                'groups_id': [(6, 0,[self.RESOURCE_CALENDAR_MANAGER.id] )]
            })
        self.tag_base = self.Tag_categories.create({'name': 'base'})
        self.tag_guest = self.Tag_categories.create({'name': 'guest'})
        self.tag_editor = self.Tag_categories.create({'name': 'editor'})
        self.tag_manager = self.Tag_categories.create({'name': 'manager'})
        self.employee_base = self.Employees.create({
                'name': 'Base User',
                'work_email': 'base@test.com',
                'user_id': self.user_base.id,
                'category_ids': [(6, 0,[self.tag_base.id])]
        })
        self.employee_guest = self.Employees.create({
                'name': 'Guest',
                'work_email': 'guest@test.com',
                'user_id': self.user_guest.id,
                'category_ids': [(6, 0,[self.tag_guest.id])]
        })
        self.employee_editor = self.Employees.create({
                'name': 'Editor',
                'work_email': 'editor@test.com',
                'user_id': self.user_editor.id,
                'category_ids': [(6, 0,[self.tag_editor.id])]
        })
        self.employee_manager = self.Employees.create({
                'name': 'Manager',
                'work_email': 'manager@test.com',
                'user_id': self.user_manager.id,
                'category_ids': [(6, 0,[self.tag_manager.id])]
        })
        self.room_base = self.Rooms.create({
            'name': 'Test Room Tag Base',
            'resource_type': 'room',
            'allow_double_book': True,
            'tag_ids': [(6, 0,[self.tag_base.id])]
        })

    def has_access_to_menu(self, user_id, menu_name):
        user = self.env['res.users'].browse(user_id)
        for group in user.groups_id:
            for m in group.menu_access:
                if m.name == menu_name:
                    return True
        return False

    def get_user_groups(self, user_id):
        user = self.env['res.users'].browse(user_id)
        return user.groups_id

    def get_group_access_rules(self, group_id):
        group = self.env['res.groups'].browse(group_id)
        return group.model_access
    
    def has_read_permission(self, access_rule):
        return access_rule.perm_read        
      
    def cannot_create_room(self, user_id, room_name):
        with self.assertRaises(exceptions.AccessError):
            self.env['resource.calendar.room'].sudo(user_id).create({'name': room_name})

    def test_010_base_user_can_not_create_rooms(self):
        self.cannot_create_room(self.user_base.id,'Room base')
    
    def test_011_guest_user_can_not_create_rooms(self):
        self.cannot_create_room(self.user_guest.id,'Room guest')
    
    def test_012_editor_user_can_not_create_rooms(self):
        self.cannot_create_room(self.user_editor.id,'Room editor')
    
    def test_013_manager_user_can_create_rooms(self):
        room_manager = self.env['resource.calendar.room'].sudo(
            self.user_manager).create({'name': 'Manager Room'})
        self.assertIsInstance(room_manager,type(self.env['resource.calendar.room']))
    
    def test_20_base_user_cannot_read_calendar_events_where_he_is_not_participant(self):
        with self.assertRaises(exceptions.AccessError):
            self.env['calendar.event'].sudo(self.user_base.id).search([])

    def test_021_base_user_can_not_create_instruments(self):
        with self.assertRaises(exceptions.AccessError):
            self.env['resource.calendar.instrument'].sudo(self.user_base.id).create({'name': 'Instrument X'})
