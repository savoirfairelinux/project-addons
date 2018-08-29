# coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class Task(models.Model):
    _name = "project.task"
    _inherit = ['project.task']

    name = fields.Char(
        string='Title',
        required=True,
    )
    code = fields.Char(
        string='Number',
    )
    activity_task_type = fields.Selection(
        [
            ('activity', 'Activity'),
            ('task', 'Task'),
        ],
        string='Type',
    )
    activity_category_id = fields.Many2one(
        'activity.category.type',
        string='Category',
    )
    task_category_id = fields.Many2one(
        'task.category.type',
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
    responsible_id = fields.Many2one(
        'res.partner',
        related='project_id.responsible_id',
        readonly=True,
        string='Responsible',
        store=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='project_id.partner_id',
        string='Client',
        store=True,
        readonly=True,
    )
    task_responsible_id = fields.Many2one(
        'res.partner',
        related='parent_id.responsible_id',
        readonly=True,
        string='Responsible',
        store=True,
    )
    task_partner_id = fields.Many2one(
        'res.partner',
        related='parent_id.partner_id',
        string='Client',
        store=True,
        readonly=True,
    )

    @api.constrains('parent_id')
    def _check_subtask_project(self):
        for task in self:
            if task.activity_task_type is False:
                super(Task, task)._check_subtask_project()

    @api.model
    def create(self, vals):
        if 'activity_task_type' in vals:
            if vals['activity_task_type'] == 'activity':
                vals['code'] = self.env['ir.sequence'] \
                    .next_by_code('project.task.activity')
            elif vals['activity_task_type'] == 'task':
                vals['code'] = self.env['ir.sequence'] \
                    .next_by_code('project.task.task')
        return super(Task, self).create(vals)
