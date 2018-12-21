# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common


class TestProjectEventCommon(common.TransactionCase):

    def setUp(self):
        super(TestProjectEventCommon, self).setUp()

        # Usefull models
        self.Partners = self.env['res.partner']
        self.Category = self.env['res.partner.category']
        self.Category_types = self.env['res.partner.category.type']
        self.Projects = self.env['project.project']
        self.Tasks = self.env['project.task']
        self.Rooms = self.env['resource.calendar.room']
        self.Instruments = self.env['resource.calendar.instrument']
        self.Task_category = self.env['task.category']

        self.client_type_1 = self.Category_types.create({
            'name': 'Client Type 1',
        })
        self.client_type_2 = self.Category_types.create({
            'name': 'Client Type 1',
        })
        self.tag_1 = self.Category.create({
            'name': 'Tag 1',
            'client_type': self.client_type_1.id,
        })
        self.tag_2 = self.Category.create({
            'name': 'Tag 1',
            'client_type': self.client_type_1.id,
        })
        self.partner_1 = self.Partners.create({
            'name': 'Partner 1',
            'tag_id': self.tag_1.id,
        })
        self.partner_2 = self.Partners.create({
            'name': 'Partner 2',
            'tag_id': self.tag_2.id,
        })
        self.responsible_1 = self.Partners.create({
            'name': 'Responsible 1',
        })
        self.responsible_2 = self.Partners.create({
            'name': 'Responsible 2',
        })
        self.category_1 = self.Task_category.create({
            'name': 'Category 1',
        })
        self.category_2 = self.Task_category.create({
            'name': 'Category 2',
        })
        self.project_1 = self.Projects.create({
            'name': 'Test Project 1',
            'responsible_id': self.responsible_1.id,
            'partner_id': self.partner_1.id,
            'project_type': 'event',
        })
        self.project_2 = self.Projects.create({
            'name': 'Test Project 2',
            'responsible_id': self.responsible_2.id,
            'partner_id': self.partner_2.id,
            'project_type': 'event',
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
        self.room_2 = self.Rooms.create({
            'name': 'Test Room 2',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.instrument_2 = self.Instruments.create({
            'name': 'Test Instrument Room 2',
            'resource_type': 'material',
            'room_id': self.room_2.id,
            'allow_double_book': True,
        })
