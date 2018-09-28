# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


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
    task_category_id = fields.Many2one(
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
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
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
