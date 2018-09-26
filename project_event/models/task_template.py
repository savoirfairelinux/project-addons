# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

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
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equipment'),
        ('room', 'Room')],
        string='Resource Type',
    )
    activity_template_id = fields.Many2one(
        'activity.template',
        default=lambda self: self.env.context.get(
           'default_activity_template_id'),
        string='Activity Template',
    )
    temp_resp_id = fields.Many2one(
        'res.partner',
        related='activity_template_id.temp_resp_id',
        readonly=True,
        string='Responsible',
        store=True,
    )
    task_category_id = fields.Many2one(
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
    )
    start_time = fields.Float(
        string='Start Time',
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.onchange('resource_type')
    def _onchange_resource_type(self):
        self.room_id = None
        self.equipment_id = None
