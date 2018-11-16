# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from odoo.addons.project_event.tests.common import TestProjectEventCommon


class TestProjectEvent(TestProjectEventCommon):

    def setUp(self):
        super(TestProjectEvent, self).setUp()
        self.AuditLogObj = self.env['auditlog.log']

        self.AuditLogObj.create({
            'model_id': self.env.ref('project.model_project_project').id,
            'res_id': self.project_1.id,
        })

    def test_010_compute_log_count(self):
        self.assertEqual(self.project_1.event_log_count, 3)
        self.project_1.name = 'Test Event Project 1'
        self.assertEqual(self.project_1.event_log_count, 4)

    def test_020_name_search(self):
        project_ids = self.Projects.name_search(
            name="Test Project 1",
            operator='ilike',
            args=[('id', '=', self.project_1.id)]
        )
        self.assertEqual(len(project_ids), 1)
