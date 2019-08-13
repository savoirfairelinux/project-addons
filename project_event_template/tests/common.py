# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common


class TestProjectEventTemplateCommon(common.TransactionCase):

    def setUp(self):
        super(TestProjectEventTemplateCommon, self).setUp()

        # Usefull models
        self.ActivityTemplate = self.env['activity.template']
        self.EventTemplates = self.env['event.template']
        self.TaskTemplate = self.env['task.template']
        self.Tasks = self.env['project.task']
        self.Partners = self.env['res.partner']
        self.Projects = self.env['project.project']
        self.Rooms = self.env['resource.calendar.room']
        self.Instruments = self.env['resource.calendar.instrument']

        self.partner_1 = self.Partners.create({
            'name': 'Partner 1',
            'email': 'test@test.com',
        })
        self.responsible_1 = self.Partners.create({
            'name': 'Responsible 1',
        })
        self.room_1 = self.Rooms.create({
            'name': 'Test Room 1',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.instrument_1 = self.Instruments.create({
            'name': 'Test Intrument Room 1',
            'resource_type': 'material',
            'room_id': self.room_1.id,
            'allow_double_book': True,
        })
        self.activity_template_1 = self.ActivityTemplate.create({
            'name': 'Activity Test Template Actions 1',
            'temp_resp_id': self.responsible_1.id,
            'room_id': self.room_1.id,
            'notes': 'Some Activity Notes ...',
        })
        self.task_template_1 = self.TaskTemplate.create({
            'name': 'Task Test Template Actions 1',
            'temp_resp_id': self.responsible_1.id,
            'room_id': self.room_1.id,
            'notes': 'Some Task Notes ...',
        })
