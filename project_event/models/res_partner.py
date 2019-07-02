# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

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

    hourly_rate = fields.Float(
        string='Hourly rate',
        digits=(3, 2),
        help='Enter the contact hourly rate')
