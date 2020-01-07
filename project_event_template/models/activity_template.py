# © 2019 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ActivityTemplate(models.Model):
    """Event Activity Template"""
    _name = "activity.template"
    _description = __doc__

    name = fields.Char(
        string='Name',
    )
    event_template_ids = fields.Many2many(
        comodel_name='event.template',
        relation='event_template_activity_template_rel',
        column1='activity_template_id',
        column2='event_template_id',
        string='Events Templates',
    )
    temp_resp_id = fields.Many2one(
        'res.partner',
        string='Responsible',
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
    duration = fields.Float(
        string='Duration',
        help="In minutes",
    )
    start_time = fields.Float(
        string='Start Time',
        help=" In minutes: value should be negative if it is before"
             " the main task (preceded by '-') or positive if it is after",
    )
    task_template_ids = fields.Many2many(
        comodel_name='task.template',
        relation='activity_template_task_template_rel',
        column1='activity_template_id',
        column2='task_template_id',
        string='Tasks Templates',
    )
    description = fields.Html(
        string='Description',
    )
    notes = fields.Html(
        string='Notes',
    )
