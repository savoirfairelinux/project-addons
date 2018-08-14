# coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class Task(models.Model):
    _name = "project.task"
    _inherit = ['project.task']

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
    activity_category = fields.Many2one(
        'activity.category.type',
        string='Category',
    )

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
