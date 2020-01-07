# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner']

    tag_id = fields.Many2one(
        'res.partner.category',
        string='Tag',
    )

    is_visible_in_technical_sheet = fields.Boolean(
        string='Is visible in Activity technical sheet',
        default=False,
    )
