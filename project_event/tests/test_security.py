# © 2019 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestProjectEventCommon
from odoo import exceptions
from odoo import fields
from datetime import datetime, timedelta


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
        self.event_vals = {
            'name': 'Event test',
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)), }
        self.PROJECT_EVENT_EDITOR.write(
            {'room_ids': [(6, 0, [self.room_1.id])]})

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
                    + self.get_crud_permissions_from_acl(a['external_id']) +\
                    "\n"

    def get_crud_permissions_from_acl(self, external_id):
        acls = ' ('
        acl = self.env.ref(external_id)
        acls += ' 1,' if acl.perm_read else ' 0,'
        acls += ' 1,' if acl.perm_write else ' 0,'
        acls += ' 1,' if acl.perm_create else ' 0,'
        acls += ' 1) ' if acl.perm_unlink else ' 0) '
        return acls

    @staticmethod
    def get_crud_rule(rule):
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

    @staticmethod
    def get_rules_applied_to_user(user):
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
        self.user_can_create_project(self.user_editor)

    def user_can_create_project(self, user):
        project_created = self.Projects.sudo(
            user.id).create({'name': 'Test Create'})
        self.assertIsInstance(
            project_created,
            type(self.Projects))

    def test_080_project_editor_can_delete_project_project(self):
        self.assertTrue(
            self.project_3.sudo(self.user_editor).unlink()
        )

    def test_090_project_manager_can_read_project_project(self):
        self.get_user_acls_and_rules_to_model(self.user_manager, self.Projects)
        self.assertEqual(
            self.Projects.search([]),
            self.Projects.sudo(self.user_manager).search([]))

    def test_100_project_manager_can_write_project_project(self):
        self.user_can_write_project(self.user_manager)

    def test_110_project_manager_can_create_project_project(self):
        self.user_can_create_project(self.user_manager)

    def test_120_project_manager_can_delete_project_project(self):
        self.assertTrue(
            self.project_3.sudo(self.user_manager).unlink()
        )

    def test_130_user_can_read_pt_type_activity(
            self):
        self.get_user_acls_and_rules_to_model(self.project_user, self.Tasks)
        self.assertEqual(
            len(self.Tasks.sudo(self.project_user.id).search([])),
            0)
        twup = self.create_task_project_user_participant()
        task_with_user_participant = twup
        self.assertEqual(
            self.Tasks.sudo(self.project_user.id).browse(
                task_with_user_participant.parent_id.id),
            self.activity_1)

    def create_task_project_user_participant(self, user_id=1):
        return self.Tasks.sudo(user_id).create({
            'name': 'Test Task User Participant',
            'activity_task_type': 'task',
            'project_id': self.project_1.id,
            'responsible_id': self.project_1.responsible_id.id,
            'partner_id': self.project_1.partner_id.id,
            'room_id': self.room_1.id,
            'parent_id': self.activity_1.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
            'employee_ids': [[6, False, [self.employee_base.id]]],
        })

    def test_140_user_can_read_pt_type_task(
            self):
        self.assertEqual(
            len(self.Tasks.sudo(self.project_user.id).search([])),
            0)
        task_with_user_participant =\
            self.create_task_project_user_participant()
        parent_activity = task_with_user_participant.parent_id
        parent_childen_ids = parent_activity.child_ids.ids
        parent_activity.do_reservation()
        self.assertEqual(
            self.Tasks.sudo(self.project_user.id).search([]).ids,
            parent_childen_ids + [parent_activity.id])

    def test_150_project_user_cannot_create_project_task(self):
        with self.assertRaises(exceptions.AccessError):
            self.Tasks.sudo(self.project_user.id).create({})

    def test_160_project_user_cannot_delete_project_task(self):
        task = self.create_task_project_user_participant()
        task.do_reservation()
        with self.assertRaises(exceptions.AccessError):
            self.Tasks.sudo(self.project_user.id).search([]).unlink()

    def test_170_project_editor_can_read_project_task(self):
        self.get_user_acls_and_rules_to_model(self.user_editor, self.Tasks)
        self.assertEqual(
            self.Tasks.sudo(self.user_editor.id).search([]),
            self.Tasks.search([]))

    def test_180_project_editor_can_write_project_task(self):
        self.assertTrue(
            self.task_1.sudo(self.user_editor.id).write({})
        )

    def test_190_project_editor_can_create_project_task(self):
        task_created = self.create_task_project_user_participant(
            self.user_editor.id)
        self.assertIsInstance(
            task_created,
            type(self.Tasks))

    def test_200_project_editor_can_delete_project_task(self):
        self.assertTrue(self.Tasks.sudo(self.user_editor.id).unlink())

    def test_210_project_manager_can_read_project_task(self):
        self.get_user_acls_and_rules_to_model(self.user_manager, self.Tasks)
        self.assertEqual(
            self.Tasks.sudo(self.user_manager.id).search([]),
            self.Tasks.search([]))

    def test_220_project_manager_can_write_project_task(self):
        self.assertTrue(
            self.task_1.sudo(self.user_manager.id).write({})
        )

    def test_230_project_manager_can_create_project_task(self):
        task_created = self.create_task_project_user_participant(
            self.user_manager.id)
        self.assertIsInstance(
            task_created,
            type(self.Tasks))

    def test_240_project_manager_can_delete_project_task(self):
        self.assertTrue(self.Tasks.sudo(self.user_manager.id).unlink())

    def test_610_project_user_can_read_project_task_category(self):

        self.get_user_acls_and_rules_to_model(
            self.project_user, self.Task_category)
        with self.assertRaises(exceptions.AccessError):
            self.Task_category.sudo(self.project_user.id).search([])

    def test_620_project_user_cannot_write_project_task_category(self):
        self.user_cannot_write_project_task_category(self.project_user)

    def user_cannot_write_project_task_category(self, user):
        with self.assertRaises(exceptions.AccessError):
            self.category_1.sudo(user.id).write(
                {'name': 'New Name'})

    def test_630_project_user_cannot_create_project_task_category(self):
        self.user_cannot_create_project_task_category(self.project_user)

    def user_cannot_create_project_task_category(self, user):
        with self.assertRaises(exceptions.AccessError):
            self.Task_category.sudo(user.id).create(
                {'name': 'New Name'})

    def test_640_project_user_cannot_delete_project_task_category(self):
        self.user_cannot_delete_project_task_category(self.project_user)

    def user_cannot_delete_project_task_category(self, user):
        with self.assertRaises(exceptions.AccessError):
            self.category_1.sudo(user.id).unlink()

    def test_650_project_editor_can_read_project_task_category(self):
        self.get_user_acls_and_rules_to_model(
            self.user_editor, self.Task_category)
        self.assertEqual(
            self.Task_category.search([]),
            self.Task_category.sudo(self.user_editor).search([]))

    def test_660_project_editor_can_write_project_task_category(self):
        self.assertTrue(self.category_1.sudo(
            self.user_editor.id).write({}))

    def test_670_project_editor_cannot_create_project_task_category(self):
        self.user_cannot_create_project_task_category(self.user_editor)

    def test_680_project_editor_cannot_delete_project_task_category(self):
        self.user_cannot_delete_project_task_category(self.user_editor)

    def test_690_project_manager_can_read_project_task_category(self):
        self.get_user_acls_and_rules_to_model(
            self.user_manager, self.Task_category)
        self.assertEqual(
            self.Task_category.search([]),
            self.Task_category.sudo(self.user_manager).search([]))

    def test_700_project_manager_can_write_project_task_category(self):
        self.assertTrue(self.category_1.sudo(self.user_manager.id).write(
            {}))

    def test_720_project_manager_can_delete_project_task_category(self):
        self.assertTrue(
            self.category_2.sudo(self.user_manager).unlink())

    def test_730_project_editor_can_read_resource_calendar_room_in_his_grps(
            self):
        self.get_user_acls_and_rules_to_model(self.user_editor, self.Rooms)
        self.assertEqual(
            self.room_1,
            self.Rooms.sudo(self.user_editor.id).search([]))

    def test_740_project_editor_cannot_write_resource_calendar_room(self):
        with self.assertRaises(exceptions.AccessError):
            self.room_1.sudo(self.user_editor.id).write(
                {'name': 'New Name'})

    def test_750_project_editor_cannot_create_resource_calendar_room(self):
        with self.assertRaises(exceptions.AccessError):
            self.Rooms.sudo(self.user_editor.id).create({})

    def test_760_project_editor_cannot_delete_resource_calendar_room(self):
        with self.assertRaises(exceptions.AccessError):
            self.Rooms.sudo(
                self.user_editor.id).browse(
                self.room_1.id).unlink()

    def test_770_project_manager_can_read_resource_calendar_room(self):
        self.get_user_acls_and_rules_to_model(self.user_manager, self.Rooms)
        self.assertEqual(
            self.Rooms.search([]),
            self.Rooms.sudo(self.user_manager).search([]))

    def test_780_project_manager_can_write_resource_calendar_room(self):
        self.assertTrue(self.room_1.sudo(self.user_manager.id).write(
            {}))

    def test_790_project_manager_can_create_resource_calendar_room(self):
        room_created = self.Rooms.sudo(
            self.user_manager.id).create({'name': 'Test Create'})
        self.assertIsInstance(
            room_created,
            type(self.Rooms))

    def test_800_project_manager_can_delete_resource_calendar_room(self):
        self.assertTrue(
            self.Rooms.sudo(self.user_manager.id).search([]).unlink()
        )

    def test_810_project_editor_can_read_resource_calendar_instrument(self):
        self.get_user_acls_and_rules_to_model(
            self.user_editor, self.Instruments)
        self.assertEqual(
            self.Instruments.search([]),
            self.Instruments.sudo(self.user_editor).search([]))

    def test_820_project_editor_cannot_write_resource_calendar_instrument(
            self):
        with self.assertRaises(exceptions.AccessError):
            self.instrument_1.sudo(self.user_editor.id).write(
                {'name': 'New Name'})

    def test_830_project_editor_cannot_create_resource_calendar_instrument(
            self):
        with self.assertRaises(exceptions.AccessError):
            self.Instruments.sudo(self.user_editor.id).create({})

    def test_840_project_editor_cannot_delete_resource_calendar_instrument(
            self):
        with self.assertRaises(exceptions.AccessError):
            self.Instruments.sudo(self.user_editor.id).search([]).unlink()

    def test_850_project_manager_can_read_resource_calendar_instrument(self):
        self.get_user_acls_and_rules_to_model(
            self.user_manager, self.Instruments)
        self.assertEqual(
            self.Instruments.search([]),
            self.Instruments.sudo(self.user_manager).search([]))

    def test_860_project_manager_can_write_resource_calendar_instrument(self):
        self.assertTrue(self.instrument_1.sudo(self.user_manager.id).write(
            {}))

    def test_870_project_manager_can_create_resource_calendar_instrument(self):
        instrument_created = self.Instruments.sudo(
            self.user_manager.id).create({'name': 'Test Create'})
        self.assertIsInstance(
            instrument_created,
            type(self.Instruments))

    def test_880_project_manager_can_delete_resource_calendar_instrument(self):
        self.assertTrue(
            self.Instruments.sudo(self.user_manager.id).search([]).unlink()
        )

    def test_890_project_user_cannot_write_calendar_event(self):
        self.get_user_acls_and_rules_to_model(self.project_user, self.Events)
        self.event_vals.update(
            {'partner_ids': [(6, 0, [self.project_user.partner_id.id])]})
        calendar_event = self.Events.sudo().\
            create(self.event_vals)
        self.assertTrue(
            calendar_event.sudo(self.user_editor.id).write({})
        )

    def test_900_project_user_cannot_create_calendar_event(self):
        with self.assertRaises(exceptions.AccessError):
            self.Events.sudo(self.project_user.id).create(self.event_vals)

    def test_910_project_user_cannot_delete_calendar_event(self):
        self.event_vals.update(
            {'partner_ids': [(6, 0, [self.project_user.partner_id.id])]})
        calendar_event = self.Events.sudo().\
            create(self.event_vals)
        with self.assertRaises(exceptions.AccessError):
            calendar_event.sudo(self.project_user.id).unlink()

    def test_920_user_editor_can_read_calendar_event(self):
        self.get_user_acls_and_rules_to_model(self.user_editor, self.Events)
        self.assertEqual(
            self.Events.sudo(self.user_editor.id).search([]),
            self.Events.search([]))

    def test_930_user_editor_can_create_calendar_event(self):
        vals = self.event_vals
        vals['client_id'] = self.user_editor.partner_id.id
        vals['partner_ids'] = [(6, 0, [self.user_editor.partner_id.id])]
        vals['room_id'] = self.room_1.id
        event_created = self.Events.sudo(
            self.user_editor.id).create(vals)
        self.assertIsInstance(
            event_created,
            type(self.Events))

    def test_940_user_editor_can_delete_calendar_event(self):
        vals = self.event_vals
        vals['client_id'] = self.user_editor.partner_id.id
        vals['partner_ids'] = [(6, 0, [self.user_editor.partner_id.id])]
        vals['room_id'] = self.room_1.id
        event_created = self.Events.sudo(
            self.user_editor.id).create(vals)
        self.assertTrue(
            event_created.unlink())

    def test_950_user_manager_can_read_calendar_event(self):
        self.get_user_acls_and_rules_to_model(self.user_manager, self.Events)
        self.assertEqual(
            self.Events.sudo(self.user_manager.id).search([]),
            self.Events.search([]))

    def test_960_user_manager_can_create_calendar_event(self):
        evemt_created = self.Events.sudo(
            self.user_manager.id).create(self.event_vals)
        self.assertIsInstance(
            evemt_created,
            type(self.Events))

    def test_970_user_manager_can_delete_calendar_event(self):
        self.assertTrue(
            self.Events.sudo(self.user_manager.id).search([]).unlink())

    def test_980_project_user_can_read_calendar_event_if_attendee(self):
        self.event_vals.update(
            {'partner_ids': [(6, 0, [self.project_user.partner_id.id])]})
        calendar_event = self.Events.sudo().\
            create(self.event_vals)
        self.assertEqual(self.Events.sudo(self.project_user.id).search([]),
                         calendar_event)

    def test_990_project_user_cannot_only_read_tasks_in_draft_state(self):
        self.assertEqual(
            len(self.Tasks.sudo(self.project_user.id).search([])),
            0)
        task_with_user_participant =\
            self.create_task_project_user_participant()
        parent_activity = task_with_user_participant.parent_id
        parent_childen_ids = parent_activity.child_ids.ids
        self.assertEqual(
            self.Tasks.sudo(self.project_user.id).search([]).ids,
            [])
        parent_activity.do_reservation()
        self.assertEqual(
            self.Tasks.sudo(self.project_user.id).search([]).ids,
            parent_childen_ids + [parent_activity.id])
