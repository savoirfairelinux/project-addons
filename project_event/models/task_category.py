# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class TaskCategory(models.Model):
    """Event Task Category"""
    _name = 'task.category'
    _description = __doc__
    _order = 'sequence, name, id'

    name = fields.Char(
        string='Name',
    )
    sequence = fields.Integer(
        string='Sequence',
    )
