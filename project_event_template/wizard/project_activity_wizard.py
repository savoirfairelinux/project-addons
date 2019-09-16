# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class ProjectActivityWizard(models.TransientModel):
    """Wizard Event Activity Creation from template"""
    _name = 'project.activity.wizard'
    _description = __doc__

    event_wizard_id = fields.Many2one(
        'project.event.wizard',
        string='Event Wizard',
    )
    template_id = fields.Many2one(
        'activity.template',
        string='Activity Template',
    )
    name = fields.Char(
        string='Activity Title',
    )
    activity_resp_id = fields.Many2one(
        'res.partner',
        string='Responsible',
    )
    activity_partner_id = fields.Many2one(
        'res.partner',
        string='Client',
    )
    activity_sector_id = fields.Many2one(
        'res.partner.sector',
        string='Faculty Sector',
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category',
    )
    room_id = fields.Many2one(
        'resource.calendar.room',
        string='Room',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Main task department',
    )
    service_id = fields.Many2one(
        'resource.calendar.service',
        string='Main task service',
    )
    duration = fields.Integer(
        string='Duration',
        help="In minutes",
    )
    date_start = fields.Datetime(
        string='Starting Date',
        help=" In minutes: value should be negative if it is before"
             " the main task (preceded by '-') or positive if it is after",
        default=fields.Datetime.now,
    )
    date_end = fields.Datetime(
        string='Ending Date',
    )
    description = fields.Html(
        string='Description',
    )
    notes = fields.Html(
        string='Notes',
    )
    task_line_ids = fields.One2many(
        'project.task.wizard',
        'activity_wiz_id',
        string='Tasks to Edit',
    )
    general_room_id = fields.Many2one(
        'resource.calendar.room',
        string='General Room',
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.name = self.template_id.name
            self.activity_resp_id = self.template_id.temp_resp_id
            self.category_id = self.template_id.category_id
            self.room_id = self.template_id.room_id
            self.department_id = self.template_id.department_id
            self.service_id = self.template_id.service_id
            self.duration = self.template_id.duration
            self.description = self.template_id.description
            self.notes = self.template_id.notes

    @api.onchange('general_room_id')
    def _onchange_general_room_id(self):
        if self.general_room_id:
            for act in self.task_line_ids:
                if act.resource_type == 'room':
                    act.room_id = self.general_room_id

    @api.multi
    def add_flexible_tasks(self):
        self.ensure_one()
        view = self.env.ref(
            'project_event_template.view_project_task_wizard_activity')

        for task in self.template_id.task_template_ids:
            task_vals = {
                'template_id': task.id,
                'activity_wiz_id': self.id,
                'task_name': task.name,
                'task_resp_id':
                self.activity_resp_id and
                self.activity_resp_id.id or
                task.temp_resp_id.id,
                'task_partner_id':
                self.activity_partner_id and
                self.activity_partner_id.id or
                False,
                'task_sector_id':
                self.activity_sector_id and
                self.activity_sector_id.id or
                False,
                'category_id': task.category_id.id,
                'resource_type': task.resource_type,
                'equipment_id': task.equipment_id.id,
                'room_id': (
                    self.room_id and self.room_id.id or task.room_id.id
                ) if task.resource_type == 'room' else False,
                'service_id': task.service_id.id,
                'department_id': task.department_id.id,
                'employee_ids': [(4, e.id) for e in task.employee_ids],
                'duration': task.duration,
                'start_time': task.start_time,
                'description': task.description,
                'notes': task.notes,
            }
            self.env['project.task.wizard'].create(task_vals)

        return {
            'name': _('Tasks Wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'views': [(view.id, 'form')],
            'target': 'new',
            'res_id': self.id,
        }

    @api.multi
    def create_activity_from_template(self):
        self.ensure_one()
        tasks = self.env['project.task.wizard'].search([
            ('activity_wiz_id', '=', self.id)])
        activity_vals = {
            'name': self.name,
            'responsible_id': self.activity_resp_id.id,
            'partner_id': self.activity_partner_id.id,
            'client_type': self.activity_partner_id.tag_id.client_type.id,
            'sector_id': self.activity_sector_id.id,
            'category_id': self.category_id.id,
            'activity_task_type': 'activity',
            'room_id': self.room_id.id,
            'department_id': self.department_id.id,
            'service_id': self.service_id.id,
            'date_start': self.date_start,
            'date_end': fields.Datetime.from_string(
                self.date_start) + relativedelta(minutes=self.duration),
            'description': self.description,
            'notes': self.notes,
            'child_ids': [
                (0,
                 0,
                 {
                     'name': task.task_name,
                     'activity_task_type': 'task',
                     'responsible_id': task.task_resp_id.id,
                     'partner_id': task.task_partner_id.id,
                     'client_type': task.task_partner_id.tag_id.client_type.id,
                     'sector_id': task.task_sector_id.id,
                     'category_id': task.category_id.id,
                     'department_id': task.department_id.id,
                     'employee_ids': [(4, e.id) for e in task.employee_ids],
                     'resource_type': task.resource_type,
                     'equipment_id': task.equipment_id.id,
                     'room_id': task.room_id.id,
                     'service_id': task.service_id.id,
                     'date_start': (
                         fields.Datetime.from_string(
                             self.date_start) + relativedelta(
                             minutes=task.start_time)
                     ),
                     'date_end': (
                         fields.Datetime.from_string(
                             self.date_start) + relativedelta(
                             minutes=task.start_time + task.duration)
                     ),
                     'notes': task.notes,
                     'description': task.description,
                 }
                 ) for task in tasks],
        }
        self.env['project.task'].create(activity_vals)
