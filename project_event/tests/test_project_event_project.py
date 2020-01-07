# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestProjectEventCommon


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

    def test_030_onchange_partner_id(self):
        self.project_1._onchange_partner_id()
        self.assertEqual(self.project_1.client_type.name, 'Client Type 1')
        self.client_type_3 = self.Category_types.create({
            'name': 'Type 3',
        })
        self.tag_1 = self.Category.create({
            'name': 'Tag 2',
            'client_type': self.client_type_3.id,
        })
        self.partner_tag2 = self.Partners.create({
            'name': 'Partner Tag 2',
            'tag_id': self.tag_1.id,
        })
        self.project_1.partner_id = self.partner_tag2.id
        self.project_1._onchange_partner_id()
        self.assertEqual(self.project_1.client_type.name, 'Type 3')

    def test_040_duplicate_project_duplicates_task_ids(self):
        new_project = self.project_1.copy()
        self.assertEqual(len(
            self.project_1.task_ids),
            len(new_project.task_ids)
        )
