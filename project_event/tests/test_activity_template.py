# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from odoo.addons.project_event.tests.common import TestProjectEventCommon


class TestActivityTemplate(TestProjectEventCommon):

    def setUp(self):
        super(TestActivityTemplate, self).setUp()

    def test_010_action_clear_and_initialise(self):
        self.activity_template_1.action_initialize()
        self.assertEqual(
            len(self.activity_template_1.task_template_ids), 2
        )
        self.activity_template_1.action_clear()
        self.assertEqual(
            len(self.activity_template_1.task_template_ids), 0
        )
