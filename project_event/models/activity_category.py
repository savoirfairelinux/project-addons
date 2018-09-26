# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ActivityCategory(models.Model):
    """Event Activity Category"""
    _name = 'activity.category'
    _description = __doc__
    _order = 'sequence, name, id'

    name = fields.Char(
        string='Name',
        translate=True,
    )
    sequence = fields.Integer(
        string='Sequence',
    )
