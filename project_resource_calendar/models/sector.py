# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class Sector(models.Model):
    _name = 'sector.sector'

    name = fields.Char(
        string='Name',
    )
