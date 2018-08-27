# coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class TaskTemplate(models.Model):
    _name = "task.template"
    _inherit = ['project.task']

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
    duration = fields.Float(
        string='Duration',
    )
    start_time = fields.Float(
        string='Start Time',
    )
