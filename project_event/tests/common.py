# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common


class TestProjectEventCommon(common.TransactionCase):

    def setUp(self):
        super(TestProjectEventCommon, self).setUp()

        # Usefull models
        self.Partners = self.env['res.partner']
        self.Projects = self.env['project.project']
        self.Rooms = self.env['resource.calendar.room']
        self.Instruments = self.env['resource.calendar.instrument']

        self.partner_1 = self.Partners.create({
            'name': 'Partner 1',
        })
        self.responsible_1 = self.Partners.create({
            'name': 'Responsible 1',
        })
        self.project_1 = self.Projects.create({
            'name': 'Test Project 1',
            'responsible_id': self.responsible_1.id,
            'partner_id': self.partner_1.id,
            'project_type': 'event',
        })
        self.room_1 = self.Rooms.create({
            'name': 'Test Room 1',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.instrument_1 = self.Instruments.create({
            'name': 'Test Room 1',
            'resource_type': 'material',
            'room_id': self.room_1.id,
            'allow_double_book': True,
        })
