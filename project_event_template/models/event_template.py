# © 2019 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventTemplate(models.Model):
    """Event Template"""
    _name = "event.template"
    _description = __doc__

    name = fields.Char(
        string='Name',
    )
    temp_resp_id = fields.Many2one(
        'res.partner',
        string='Responsible',
    )
    activity_template_ids = fields.Many2many(
        comodel_name='activity.template',
        relation='event_template_activity_template_rel',
        column1='event_template_id',
        column2='activity_template_id',
        string='Activities Templates',
    )
    description = fields.Html(
        string='Description',
    )
    notes = fields.Html(
        string='Notes',
    )
