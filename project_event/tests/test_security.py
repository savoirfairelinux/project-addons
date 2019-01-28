# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.addons.project_event.tests.common import TestProjectEventCommon


class TestSecurity(TestProjectEventCommon):

    def setUp(self):
        super(TestSecurity, self).setUp()
        self.PROJECT_EVENT_USER = self.env.ref(
            'project_event.group_project_event_user')
        self.PROJECT_EVENT_EDITOR = self.env.ref(
            'project_event.group_project_event_editor')
        self.PROJECT_EVENT_MANAGER = self.env.ref(
            'project_event.group_project_event_manager')
        self.Users = self.env['res.users']
        self.Employees = self.env['hr.employee']
        self.project_user = self.Users.create({
            'name': 'User',
            'login': 'base@test.com',
            'groups_id': [(6, 0, [self.PROJECT_EVENT_USER.id])]
        })
        self.user_editor = self.Users.create({
            'name': 'Editor',
            'login': 'editor@test.com',
            'groups_id': [(6, 0, [self.PROJECT_EVENT_EDITOR.id])]
        })
        self.user_manager = self.Users.create({
            'name': 'Manager',
            'login': 'manager@test.com',
            'groups_id': [(6, 0, [self.PROJECT_EVENT_MANAGER.id])]
        })
        self.employee_base = self.Employees.create({
            'name': 'User',
            'work_email': 'base@test.com',
            'user_id': self.project_user.id
        })
        self.employee_editor = self.Employees.create({
            'name': 'Editor',
            'work_email': 'editor@test.com',
            'user_id': self.user_editor.id
        })
        self.employee_manager = self.Employees.create({
            'name': 'Manager',
            'work_email': 'manager@test.com',
            'user_id': self.user_manager.id
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
