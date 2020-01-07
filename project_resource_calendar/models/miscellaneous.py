# Copyright 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Miscellaneous(models.Model):
    _name = 'resource.calendar.miscellaneous'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
    )
    sequence = fields.Integer(
        string='Sequence',
    )
