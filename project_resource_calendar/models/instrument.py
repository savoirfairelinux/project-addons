# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Instrument(models.Model):
    """Resource Calendar Instrument"""
    _name = 'resource.calendar.instrument'
    _inherit = ['resource.resource']
    _description = __doc__

    sku = fields.Char(
        string='SKU',
    )
    room_id = fields.Many2one(
        'resource.calendar.room',
        string='Room',
    )
    category_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('consumable', 'Consumable'),
        ('instrument', 'Instrument'),
        ('service', 'Service'),
        ],
        string='Type',
        index=True,
        default='instrument',
    )
