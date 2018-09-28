# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class Miscellaneous(models.Model):
    _name = 'resource.calendar.miscellaneous'

    name = fields.Char(
        string='Name',
    )
