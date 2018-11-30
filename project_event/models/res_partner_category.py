# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PartnerCategory(models.Model):
    _inherit = ['res.partner.category']

    client_type = fields.Many2one(
        'res.partner.category.type',
        string='Client Type',
        track_visibility='onchange',
    )
