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
        self.user_editor.partner_id.write({'email': 'editor@test.com'})
        self.user_manager.partner_id.write({'email': 'manager@test.com'})

    def get_user_acls_and_rules_to_model(self, user, model):
        rules = self.get_rules_applied_to_user_and_model(user, model)
        acls = self.get_user_s_access_list_to_model(user.id, model)
        self.print_user_acls_and_rules_to_model(user, rules, acls, model)

    def get_rules_applied_to_user_and_model(self, user, model):
        rules_user_model = []
        for rule_model in self.get_rules_applied_to_model(model):
            rules_groups = self.get_rules_applied_to_user(user)
            for group in rules_groups:
                if rule_model in group['rules']:
                    rules_user_model.append((rule_model, group['group']))
        return rules_user_model

    def get_user_s_access_list_to_model(self, user_id, model):
        user_acls = {}
        for group in self.get_user_groups(user_id):
            acls = self.get_group_s_access_list_to_model(group, model)
            if acls:
                user_acls[str(acls.pop('group'))] = acls
        return user_acls

    def print_user_acls_and_rules_to_model(self, user, rules, acls, model):
        ir_model = self.get_ir_model_from_model(model)
        message = "User " + user.name + " (" + str(user) + ")"\
            + " has acls to model " + ir_model.name + \
            " (" + str(model) + ")" + ': \n'
        for group, acl in acls.items():
            message += "Group: " + group
            for rule in rules:
                if rule[1] == group:
                    message += "--> Rule: " + self.get_crud_rule(rule[0])\
                        + str(rule[0])\
                        + "(" + rule[0].domain_force + ")"
            message += "\n"
            for a in acl['acls']:
                message += "\t External id: " + a['external_id']\
                    + self.get_crud_permissions_from_acl(a['external_id']) + "\n"
        print(message)

    def get_crud_permissions_from_acl(self, external_id):
        acls = ' ('
        acl = self.env.ref(external_id)
        acls += ' 1,' if acl.perm_read else ' 0,'
        acls += ' 1,' if acl.perm_write else ' 0,'
        acls += ' 1,' if acl.perm_create else ' 0,'
        acls += ' 1) ' if acl.perm_unlink else ' 0) '
        return acls

    def get_crud_rule(self, rule):
        rule_crud = ' ('
        rule_crud += ' 1,' if rule.perm_read else ' 0,'
        rule_crud += ' 1,' if rule.perm_write else ' 0,'
        rule_crud += ' 1,' if rule.perm_create else ' 0,'
        rule_crud += ' 1) ' if rule.perm_unlink else ' 0) '
        return rule_crud

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
        if not group_access['acls']:
            return
        return group_access

    def get_rules_applied_to_model(self, model):
        ir_model = self.get_ir_model_from_model(model)
        return self.env['ir.rule'].search([('model_id', '=', ir_model.id)])

    def get_rules_applied_to_user(self, user):
        rules = []
        for group in user.groups_id:
            rules.append({
                'group': group.name,
                'rules': group.rule_groups})
        return rules

    def get_ir_model_from_model(self, model):
        name = str(model).replace('(', '').replace(')', '')
        return self.env['ir.model'].search([('model', '=', name)])

    def test_010_project_user_cannot_read_project_project(self):
        self.get_user_acls_and_rules_to_model(self.project_user, self.Projects)
        with self.assertRaises(exceptions.AccessError):
            self.Projects.sudo(self.project_user.id).search([])

    def test_020_project_user_cannot_create_project_project(self):
        with self.assertRaises(exceptions.AccessError):
            self.Projects.sudo(self.project_user.id).create({})

    def test_030_proejct_user_cannot_delete_project_project(self):
        with self.assertRaises(exceptions.AccessError):
            self.Projects.sudo(self.project_user.id).search([]).unlink()

    def test_040_project_user_cannot_write_project_project(self):
        with self.assertRaises(exceptions.AccessError):
            self.project_1.sudo(self.project_user.id).write(
                {'name': 'New Name'})

    def test_050_project_editor_can_read_project_project(self):
        self.get_user_acls_and_rules_to_model(self.user_editor, self.Projects)
        self.assertEqual(
            self.Projects.search([]),
            self.Projects.sudo(self.user_editor).search([]))

    def test_060_project_editor_can_write_project_project(self):
        self.user_can_write_project(self.user_editor)

    def user_can_write_project(self, user):
        self.project_1.sudo(user.id).write(
            {'name': 'Test Project 1060'})
        self.assertEqual(
            self.project_1.name,
            'Test Project 1060'
        )
        self.project_1.write({'name': 'Test Project 1'})

    def test_070_project_editor_can_create_project_project(self):
        self.user_can_create_project(self.editor_user)

    def user_can_create_project(self, user):
        project_created = self.Projects.sudo(
            user.id).create({'name': 'Test Create'})
        self.assertIsInstance(
            project_created,
            type(self.Projects))

    def test_080_project_editor_can_delete_project_project(self):
        self.assertTrue(
            self.project_1.sudo(self.user_editor).unlink()
        )

    def test_050_project_manager_can_read_project_project(self):
        self.get_user_acls_and_rules_to_model(self.user_manager, self.Projects)
        self.assertEqual(
            self.Projects.search([]),
            self.Projects.sudo(self.user_manager).search([]))

    def test_060_project_manager_can_write_project_project(self):
        self.user_can_write_project(self.user_manager)

    def test_070_project_manager_can_create_project_project(self):
        self.user_can_create_project(self.user_manager)

    def test_080_project_manager_can_delete_project_project(self):
        self.assertTrue(
            self.project_1.sudo(self.user_manager).unlink()
        )
