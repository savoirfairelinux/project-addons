# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PartnerSector(models.Model):
    _name = 'res.partner.sector'

    name = fields.Char(
        string='Sector Type',
        translate=True,
    )
