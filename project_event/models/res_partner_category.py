# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerCategory(models.Model):
    _inherit = ['res.partner.category']

    client_type = fields.Many2one(
        'res.partner.category.type',
        string='Client Type',
    )
