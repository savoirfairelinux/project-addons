# coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class TaskCategoryType(models.Model):
    _name = 'task.category.type'
    _order = 'sequence, name, id'

    name = fields.Char(
        string='Name',
    )
    sequence = fields.Integer(
        string='Sequence'
    )
