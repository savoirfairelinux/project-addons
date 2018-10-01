# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class Room(models.Model):
    _inherit = ['resource.resource']
    _name = 'resource.calendar.room'

    room_code = fields.Char(
        string='Room ID',
    )
    capacity = fields.Integer(
        string='Capacity',
    )
    floor = fields.Char(
        string='Floor',
    )
    description = fields.Text(
        string='Dsescription',
    )
    room_type_id = fields.Many2one(
        string='Room Type',
        comodel_name='resource.calendar.room.type',
        ondelete='set null',
    )
    is_bookable = fields.Boolean(
        string='Is Bookable',
    )
    sector_id = fields.Many2one(
        string='Sector',
        comodel_name='sector.sector',
        ondelete='set null',
    )
    instruments_ids = fields.One2many(
        'resource.calendar.instrument',
        'room_id',
        string='Instruments',
    )
    miscellaneous = fields.Many2many(
        string='Miscellaneous',
        comodel_name='resource.calendar.miscellaneous',
    )
    pricing = fields.Float(
        string='Pricing ($)',
    )
    pricing_type = fields.Char(
        string='Pricing_type',
    )

    @api.model
    def create(self, values):
        """
            Create a new record for a model Room
            @param values: provides a data for new record
            @return: returns a id of new record
        """
        values['resource_type'] = 'room'
        result = super().create(values)
        return result
