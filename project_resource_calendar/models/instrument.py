# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Instrument(models.Model):
    """Resource Calendar Instrument"""
    _name = 'resource.calendar.instrument'
    _inherit = ['resource.resource']
    _description = __doc__

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
    )
    tarification = fields.Monetary(
        'tarification',
         currency_field='currency_id',
    )
    photos = fields.Binary(
        "Photo",
        help="Add Instrument Photo",
    )
    group_ids = fields.Many2many(
        'res.groups',
        string='Group Type',
    )
    sku = fields.Char(
        string='SKU',
    )
    room_id = fields.Many2one(
        'resource.calendar.room',
        string='Room',
    )
    category_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('consumables', 'Consumables'),
        ('instruments', 'Instruments'),
        ('services', 'Services'),
        ],
        string='Type',
        index=True,
        copy=False,
        default='equipment',
    )
