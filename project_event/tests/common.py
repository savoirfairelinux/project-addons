# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common
from datetime import datetime, timedelta
from odoo import fields


class TestProjectEventCommon(common.TransactionCase):

    def setUp(self):
        super(TestProjectEventCommon, self).setUp()

        # Usefull models
        self.ActivityTemplate = self.env['activity.template']
        self.EventTemplates = self.env['event.template']
        self.TaskTemplate = self.env['task.template']
        self.Tasks = self.env['project.task']
        self.Partners = self.env['res.partner']
        self.Category = self.env['res.partner.category']
        self.Category_types = self.env['res.partner.category.type']
        self.Projects = self.env['project.project']
        self.Tasks = self.env['project.task']
        self.Rooms = self.env['resource.calendar.room']
        self.Instruments = self.env['resource.calendar.instrument']
        self.Task_category = self.env['task.category']
        self.Department = self.env['hr.department']
        self.Sector = self.env['res.partner.sector']
        self.Events = self.env['calendar.event']
        self.Employee = self.env['hr.employee']
        self.User = self.env['res.users']
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
            'name': 'Tag 2',
            'client_type': self.client_type_2.id,
        })
        self.partner_1 = self.Partners.create({
            'name': 'Partner 1',
            'tag_id': self.tag_1.id,
            'email': 'test@test.com',
        })
        self.partner_2 = self.Partners.create({
            'name': 'Partner 2',
            'tag_id': self.tag_2.id,
        })
        self.partner_3 = self.Partners.create({
            'name': 'Partner 3',
        })
        self.user_1 = self.User.create({
            'name': 'Partner 1',
            'login': 'base1@test.com',
            'partner_id': self.partner_1.id,
        })
        self.employee_1 = self.Employee.create({
            'name': 'Partner 1',
            'user_id': self.user_1.id,
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
        self.project_3 = self.Projects.create({
            'name': 'Test Project 3',
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

        self.department_1 = self.Department.create({
            'name': 'Department 1'
        })
        self.activity_1 = self.Tasks.create({
            'name': 'Test Activity 1',
            'activity_task_type': 'activity',
            'project_id': self.project_1.id,
            'responsible_id': self.project_1.responsible_id.id,
            'partner_id': self.project_1.partner_id.id,
            'category_id': self.category_1.id,
            'room_id': self.room_1.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
        })
        self.activity_2 = self.Tasks.create({
            'name': 'Test Activity 2',
            'activity_task_type': 'activity',
            'responsible_id': self.responsible_2.id,
            'partner_id': self.partner_2.id,
            'category_id': self.category_2.id,
            'room_id': self.room_2.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(
                datetime.today() + timedelta(hours=4)
            ),
        })
        self.activity_3 = self.Tasks.create({
            'name': 'Test Activity 3',
            'activity_task_type': 'activity',
            'project_id': self.project_1.id,
            'responsible_id': self.project_1.responsible_id.id,
            'partner_id': self.project_1.partner_id.id,
            'category_id': self.category_1.id,
            'room_id': self.room_1.id,
            'spectators': '-',
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
        })
        self.task_1 = self.Tasks.create({
            'name': 'Test task 1',
            'activity_task_type': 'task',
            'responsible_id': self.responsible_1.id,
            'partner_id': self.partner_1.id,
            'client_type': self.partner_1.tag_id.client_type.id,
            'category_id': self.category_1.id,
            'room_id': self.room_1.id,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
        })
        self.task_2 = self.Tasks.create({
            'name': 'Test Task 2',
            'activity_task_type': 'task',
            'project_id': self.project_1.id,
            'responsible_id': self.project_1.responsible_id.id,
            'partner_id': self.project_1.partner_id.id,
            'client_type': self.partner_1.tag_id.client_type.id,
            'room_id': self.room_1.id,
            'parent_id': None,
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
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
