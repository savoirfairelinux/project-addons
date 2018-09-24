# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class Instrument(models.Model):
    _inherit = ['resource.resource']
    _name = 'resource.calendar.instrument'

    room_id = fields.Many2one(
        'resource.calendar.room',
        string='Room',
        )
    resource_ids = fields.One2many(
        string='Resources',
        comodel_name='resource.resource',
        inverse_name='name',
    )
    sku = fields.Char(
        string='SKU',
    )
    item_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('instruments', 'Instruments'),
        ('services', 'Services'),
        ('consumables', 'Consumables'),
        ], string='Type', index=True, copy=False, default='equipment', track_visibility='onchange')
