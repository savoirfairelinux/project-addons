# coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ActivityTemplate(models.Model):
    _name = "activity.template"
    _inherit = ['project.task']

    event_template_id = fields.Many2one(
        'project.template',
        string='Event Template',
    )
    temp_resp_id = fields.Many2one(
        'res.partner',
        related='event_template_id.temp_resp_id',
        readonly=True,
        string='Responsible',
        store=True,
    )
    task_template_ids = fields.One2many(
        'task.template',
        'activity_template_id',
        string='Tasks Template',
    )
