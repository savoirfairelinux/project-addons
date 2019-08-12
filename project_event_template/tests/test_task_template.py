# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from .common import TestProjectEventTemplateCommon


class TestTaskTemplate(TestProjectEventTemplateCommon):

    def setUp(self):
        super(TestTaskTemplate, self).setUp()

    def test_010_onchange_resource_type(self):
        self.task_template_1._onchange_resource_type()
        self.assertEqual(self.task_template_1.room_id.id, False)
        self.assertEqual(self.task_template_1.equipment_id.id, False)
