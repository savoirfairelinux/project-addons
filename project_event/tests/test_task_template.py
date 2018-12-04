# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from odoo.addons.project_event.tests.common import TestProjectEventCommon


class TestTaskTemplate(TestProjectEventCommon):

    def setUp(self):
        super(TestTaskTemplate, self).setUp()
        self.TaskTemplate = self.env['task.template']
        self.task_template_action_1 = self.TaskTemplate.create({
            'name': 'Task Test Template Actions 1',
            'temp_resp_id': self.responsible_1.id,
            'room_id': self.room_1.id,
            'notes': 'Some Task Notes ...',
        })

    def test_010_onchange_resource_type(self):
        self.task_template_action_1._onchange_resource_type()
        self.assertEqual(self.task_template_action_1.room_id.id, False)
        self.assertEqual(self.task_template_action_1.equipment_id.id, False)
