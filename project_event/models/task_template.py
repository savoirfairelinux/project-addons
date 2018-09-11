# coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class TaskTemplate(models.Model):
    _name = "task.template"

    name = fields.Char(
        string='Name',
    )
    activity_template_id = fields.Many2one(
        'activity.template',
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
        'hr.employee', 'task_emp_rel',
        'task_id', 'employee_id',
        string='Employees'
    )
    duration = fields.Float(
        string='Duration',
    )
    start_time = fields.Float(
        string='Start Time',
    )
    notes = fields.Text(string='Notes')

