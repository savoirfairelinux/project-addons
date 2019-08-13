# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from .common import TestProjectEventTemplateCommon


class TestEventCreationFromWizard(TestProjectEventTemplateCommon):

    def setUp(self):
        super(TestEventCreationFromWizard, self).setUp()

        self.event_template1 = self.EventTemplates.create({
            'name': 'Event Test Template 1',
            'temp_resp_id': self.responsible_1.id,
            'notes': 'Some Event Notes ...',
        })
        self.activity_template1 = self.ActivityTemplate.create({
            'name': 'Activity Test Template 1',
            'event_template_ids': [(6, 0, [self.event_template1.id])],
            'temp_resp_id': self.responsible_1.id,
            'room_id': self.room_1.id,
            'notes': 'Some Activity Notes ...',
        })
        self.task_template1 = self.TaskTemplate.create({
            'name': 'Task Test Template 1',
            'temp_resp_id': self.responsible_1.id,
            'room_id': self.room_1.id,
            'resource_type': 'room',
            'activity_template_ids': [(6, 0, [self.activity_template1.id])],
            'notes': 'Some Task Notes ...',
        })
        self.task_template2 = self.TaskTemplate.create({
            'name': 'Task Test Template 2',
            'temp_resp_id': self.responsible_1.id,
            'equipment_id': self.instrument_1.id,
            'resource_type': 'equipment',
            'activity_template_ids': [(6, 0, [self.activity_template1.id])],
            'notes': 'Some Task Notes ...',
        })

    def test_010_onchange_template_id(self):
        wiz = self.env['project.event.wizard'].create({
            'name': 'test',
            'event_resp_id': self.partner_1.id,
            'event_notes': 'Notes',
        })
        wiz.template_id = self.event_template1
        wiz._onchange_template_id()
        self.assertEqual(wiz.name, self.event_template1.name)
        self.assertEqual(wiz.event_resp_id, self.event_template1.temp_resp_id)
        self.assertEqual(wiz.event_notes, self.event_template1.notes)

    def test_020_create_event_from_template(self):
        wiz = self.env['project.event.wizard'].create({
            'template_id': self.event_template1.id,
            'event_partner_id': self.partner_1.id,
        })
        wiz._onchange_template_id()
        wiz.add_flex_activities()
        self.assertEqual(len(wiz.activity_ids), 1)
        wiz.add_flexible_tasks()
        self.assertEqual(len(wiz.task_line_ids), 2)
        # check event is created
        wiz.create_event_from_template()
        project_ids = self.Projects.search([
            ('name', '=', "Event Test Template 1"),
            ('responsible_id', '=', self.responsible_1.id),
            ('project_type', '=', 'event'),
            ('notes', '=', self.event_template1.notes),
        ])
        self.assertEqual(len(project_ids), 1)
        # check activity is created
        activity_ids = self.Tasks.search([
            ('name', '=', "Activity Test Template 1"),
            ('project_id', '=', project_ids[0].id),
            ('responsible_id', '=', self.responsible_1.id),
            ('room_id', '=', self.room_1.id),
            ('activity_task_type', '=', 'activity'),
            ('notes', '=', self.activity_template1.notes),
        ])
        self.assertEqual(len(project_ids[0].task_ids), 1)
        self.assertEqual(len(activity_ids), 1)
        # check tasks are created
        self.assertEqual(len(project_ids[0].task_ids.child_ids), 3)
        task_ids = self.Tasks.search([
            ('name', '=', "Task Test Template 1"),
            ('parent_id', '=', activity_ids[0].id),
            ('responsible_id', '=', self.responsible_1.id),
            ('room_id', '=', self.room_1.id),
            ('activity_task_type', '=', 'task'),
            ('notes', '=', self.task_template1.notes),
        ])
        self.assertEqual(len(task_ids), 1)

    def test_030_create_orphan_task(self):
        wiz = self.env['project.task.wizard'].create({
            'template_id': self.task_template1.id,
            'task_partner_id': self.partner_1.id,
        })
        wiz._onchange_template_id()
        wiz.create_orphan_task()
        task_ids = self.Tasks.search([
            ('name', '=', "Task Test Template 1"),
            ('responsible_id', '=', self.task_template1.temp_resp_id.id),
            ('activity_task_type', '=', 'task'),
            ('room_id', '=', self.room_1.id),
            ('activity_task_type', '=', 'task'),
            ('partner_id', '=', self.partner_1.id),
            ('category_id', '=', self.task_template1.category_id.id),
            ('resource_type', '=', self.task_template1.resource_type),
            ('description', '=', self.task_template1.description),
            ('notes', '=', self.task_template1.notes),
        ])
        self.assertEqual(len(task_ids), 1)

    def test_040_create_orphan_activity(self):
        wiz = self.env['project.activity.wizard'].create({
            'template_id': self.activity_template1.id,
            'activity_partner_id': self.partner_1.id,
        })
        wiz._onchange_template_id()
        wiz.add_flexible_tasks()
        self.assertEqual(len(wiz.task_line_ids), 2)
        wiz.create_activity_from_template()
        activity_ids = self.Tasks.search([
            ('name', '=', "Activity Test Template 1"),
            ('responsible_id', '=', self.responsible_1.id),
            ('room_id', '=', self.room_1.id),
            ('activity_task_type', '=', 'activity'),
            ('notes', '=', self.activity_template1.notes),
        ])
        self.assertEqual(len(activity_ids), 1)
        # check tasks are created
        self.assertEqual(len(activity_ids[0].child_ids), 3)
        task_ids = self.Tasks.search([
            ('name', '=', "Task Test Template 1"),
            ('parent_id', '=', activity_ids[0].id),
            ('responsible_id', '=', self.responsible_1.id),
            ('room_id', '=', self.room_1.id),
            ('activity_task_type', '=', 'task'),
            ('notes', '=', self.task_template1.notes),
        ])
        self.assertEqual(len(task_ids), 1)
