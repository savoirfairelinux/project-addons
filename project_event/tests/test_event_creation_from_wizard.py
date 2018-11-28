# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from odoo.addons.project_event.tests.common import TestProjectEventCommon


class TestEventCreationFromWizard(TestProjectEventCommon):

    def setUp(self):
        super(TestEventCreationFromWizard, self).setUp()
        self.EventTemplate = self.env['event.template']
        self.ActivityTemplate = self.env['activity.template']
        self.TaskTemplate = self.env['task.template']

        self.event_template1 = self.EventTemplate.create({
            'name': 'Event Test Template 1',
            'temp_resp_id': self.responsible_1.id,
            'notes': 'Some Event Notes ...',
        })
        self.activity_template1 = self.ActivityTemplate.create({
            'name': 'Activity Test Template 1',
            'event_template_id': self.event_template1.id,
            'temp_resp_id': self.responsible_1.id,
            'room_id': self.room_1.id,
            'notes': 'Some Activity Notes ...',
        })
        self.task_template1 = self.TaskTemplate.create({
            'name': 'Task Test Template 1',
            'temp_resp_id': self.responsible_1.id,
            'room_id': self.room_1.id,
            'resource_type': 'room',
            'activity_template_id': self.activity_template1.id,
            'notes': 'Some Task Notes ...',
        })
        self.task_template2 = self.TaskTemplate.create({
            'name': 'Task Test Template 2',
            'temp_resp_id': self.responsible_1.id,
            'equipment_id': self.instrument_1.id,
            'resource_type': 'equipment',
            'activity_template_id': self.activity_template1.id,
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
        wiz.add_activities()
        self.assertEqual(len(wiz.activity_ids), 1)
        wiz.add_tasks()
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
            ('is_from_template', '=', True),
        ])
        self.assertEqual(len(project_ids[0].task_ids), 1)
        self.assertEqual(len(activity_ids), 1)
        # check tasks are created
        self.assertEqual(len(project_ids[0].task_ids.child_ids), 2)
        task_ids = self.Tasks.search([
            ('name', '=', "Task Test Template 1"),
            ('parent_id', '=', activity_ids[0].id),
            ('responsible_id', '=', self.responsible_1.id),
            ('room_id', '=', self.room_1.id),
            ('activity_task_type', '=', 'task'),
            ('notes', '=', self.task_template1.notes),
            ('is_from_template', '=', True),
        ])
        self.assertEqual(len(task_ids), 1)
