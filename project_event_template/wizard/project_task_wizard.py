# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ProjectTaskWizard(models.TransientModel):
    """Wizard Event Task Creation from template"""
    _name = 'project.task.wizard'
    _description = __doc__

    event_wizard_id = fields.Many2one(
        'project.event.wizard',
        string='Event Wizard',
    )
    activity_wiz_id = fields.Many2one(
        'project.activity.wizard',
        string='Activity wizard',
    )
    activity_template_id = fields.Many2one(
        'activity.template',
        string='Activity Template',
    )
    template_id = fields.Many2one(
        'task.template',
        string='Task Template',
    )
    task_name = fields.Char(
        string='Task Title',
    )
    task_resp_id = fields.Many2one(
        'res.partner',
        string='Responsible',
    )
    task_partner_id = fields.Many2one(
        'res.partner',
        string='Client',
    )
    task_sector_id = fields.Many2one(
        'res.partner.sector',
        string='Faculty Sector',
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category',
    )
    room_id = fields.Many2one(
        string='Room',
        comodel_name='resource.calendar.room',
        ondelete='set null',
    )
    equipment_id = fields.Many2one(
        string='Equipment',
        comodel_name='resource.calendar.instrument',
        ondelete='set null',
    )
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equipment'),
        ('room', 'Room')],
        string='Resource Type',
    )
    service_id = fields.Many2one(
        string='Service',
        comodel_name='resource.calendar.service',
        ondelete='set null',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
    )
    employee_ids = fields.Many2many(
        'hr.employee', 'task_template_wiz_emp_rel',
        'project_task_wizard_id', 'employee_id',
        string='Employees',
    )
    duration = fields.Integer(
        string='Duration',
        help="In minutes",
    )
    start_time = fields.Integer(
        string='Start Time',
        help=" In minutes: value should be negative if it is before"
             " the main task (preceded by '-') or positive if it is after",
    )
    notes = fields.Html(
        string='Notes',
    )
    description = fields.Html(
        string='Description',
    )
    date_start = fields.Datetime(
        string='Starting Date',
        default=fields.Datetime.now,
    )
    date_end = fields.Datetime(
        string='Ending Date',
    )
    service_id = fields.Many2one(
        string='Service',
        comodel_name='resource.calendar.service',
        ondelete='set null',
        track_visibility='onchange',
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.task_name = self.template_id.name
            self.task_resp_id = self.template_id.temp_resp_id
            self.category_id = self.template_id.category_id
            self.resource_type = self.template_id.resource_type
            self.room_id = self.template_id.room_id
            self.equipment_id = self.template_id.equipment_id
            self.department_id = self.template_id.department_id
            self.employee_ids = self.template_id.employee_ids
            self.duration = self.template_id.duration
            self.start_time = self.template_id.start_time
            self.description = self.template_id.description
            self.notes = self.template_id.notes
            self.service_id = self.template_id.service_id

    @api.multi
    def create_orphan_task(self):
        self.ensure_one()
        task_vals = {
            'name': self.task_name,
            'responsible_id': self.task_resp_id.id,
            'partner_id': self.task_partner_id.id,
            'client_type': self.task_partner_id.tag_id.client_type.id,
            'sector_id': self.task_sector_id.id,
            'category_id': self.category_id.id,
            'resource_type': self.resource_type,
            'department_id': self.department_id.id,
            'employee_ids': [(4, e.id) for e in self.employee_ids],
            'date_start': self.date_start,
            'date_end': self.date_end,
            'description': self.description,
            'notes': self.notes,
            'activity_task_type': 'task',
            'service_id': self.service_id.id
        }
        if self.resource_type:
            if self.resource_type == 'room':
                task_vals['room_id'] = self.room_id.id
            if self.resource_type == 'equipment':
                task_vals['equipment_id'] = self.equipment_id.id
        self.env['project.task'].create(task_vals)
