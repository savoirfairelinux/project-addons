# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.addons.project_event.tests.common import TestProjectEventCommon
from odoo import exceptions


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

    def get_group_s_access_list_to_model(self, group, model):
        ir_model = self.get_ir_model_from_model(model)
        group_access = {
            'group': group.name,
            'model': ir_model.name,
            'acls': []}
        for model_access in group.model_access:
            if model_access.model_id.id == ir_model.id:
                group_access['acls'].append({
                    'name': model_access.name,
                    'external_id': list(
                        model_access.get_external_id().values())[0]})
        if group_access['acls']:
            return
        return group_access

    def get_user_s_access_list_to_model(self, user_id, model):
        user_acls = {}
        for group in self.get_user_groups(user_id):
            acls = self.get_group_s_access_list_to_model(group, model)
            if acls:
                user_acls[str(acls.pop('group'))] = acls
        return user_acls

    def get_rules_applied_to_model(self, model):
        ir_model = self.get_ir_model_from_model(model)
        return self.env['ir.rule'].search([('model_id', '=', ir_model.id)])

    def get_group_access_rules(self, group_id):
        group = self.env['res.groups'].browse(group_id)
        return group.model_access

    def get_ir_model_from_model(self, model):
        name = str(self.Projects).replace('(', '').replace(')', '')
        return self.env['ir.model'].search([('model', '=', name)])

    def create_project_project(self):
        return False

    def test_010_project_user_cannot_read_project_project(self):
        with self.assertRaises(exceptions.AccessError):
            self.Projects.sudo(self.project_user.id).search([])

    def test_020_project_user_cannot_write_project_project(self):
        with self.asserRaises(exceptions.AccessError):
            self.Projects.sudo(self.project_user.id).write({})

    def test_030_project_user_cannot_create_project_project(self):
        with self.asserRaise(exceptions.AccessError):
            self.Projects.sudo(self.project_user.id).create()

    def test_040_proejct_user_cannot_delete_project_project(self):
        with self.assertAccessError(exceptions.AccessErro):
            self.Projects.sudo(self.project_user.id).search([]).unlink()
