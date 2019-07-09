# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Groups(models.Model):
    _inherit = "res.groups"

    room_ids = fields.Many2many(
        'resource.calendar.room', 'room_group_rel',
        'group_id', 'room_id',
        string='Rooms'
    )
