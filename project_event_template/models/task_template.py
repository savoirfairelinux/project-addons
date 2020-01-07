# © 2019 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TaskTemplate(models.Model):
    """Event Task Template"""
    _name = "task.template"
    _description = __doc__

    name = fields.Char(
        string='Name',
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
    service_id = fields.Many2one(
        string='Service',
        comodel_name='resource.calendar.service',
        ondelete='set null',
    )
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equipment'),
        ('room', 'Room')],
        string='Resource Type',
    )
    activity_template_ids = fields.Many2many(
        comodel_name='activity.template',
        relation='activity_template_task_template_rel',
        column1='task_template_id',
        column2='activity_template_id',
        string='Activities Templates',
    )
    temp_resp_id = fields.Many2one(
        'res.partner',
        string='Responsible',
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
    )
    employee_ids = fields.Many2many(
        'hr.employee', 'task_template_emp_rel',
        'task_id', 'employee_id',
        string='Employees',
    )
    duration = fields.Float(
        string='Duration',
        help="In minutes",
    )
    start_time = fields.Float(
        string='Start Time',
        help=" In minutes: value should be negative if it is before"
             " the main task (preceded by '-') or positive if it is after",
    )
    description = fields.Html(
        string='Description',
    )
    notes = fields.Html(
        string='Notes',
    )
    is_main_task = fields.Boolean(
        string='Is Main Task',
        default=False,
    )

    @api.onchange('resource_type')
    def _onchange_resource_type(self):
        self.room_id = None
        self.equipment_id = None
        self.service_id = None
