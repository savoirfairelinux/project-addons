# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class Resource(models.Model):
    _inherit = 'resource.resource'

    resource_type = fields.Selection([
        ('user', 'Human'),
        ('material', 'Material'),
        ('room', 'Room')], string='Resource Type',
        default='user', required=True)
