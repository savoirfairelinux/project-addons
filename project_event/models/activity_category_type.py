# coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ActivityCategoryType(models.Model):
    _name = 'activity.category.type'
    _order = 'sequence, name, id'

    name = fields.Char(
        string='Name',
        translate=True,
    )
    sequence = fields.Integer(
        string='Sequence'
    )
