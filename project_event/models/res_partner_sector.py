# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerSector(models.Model):
    _name = 'res.partner.sector'

    name = fields.Char(
        string='Sector Type',
        translate=True,
    )
