# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Resource(models.Model):
    _inherit = 'resource.resource'

    resource_type = fields.Selection([
        ('user', 'Human'),
        ('material', 'Material'),
        ('room', 'Room')
    ],
        string='Resource Type',
        default='user',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )
    is_bookable = fields.Boolean(
        string='Is Bookable',
    )
    photo = fields.Binary(
        "Photo",
        help="Add Photo",
        attachment=True,
    )
    photo_1 = fields.Binary(
        "Photo 1",
        help="Add Photo",
        attachment=True,
    )
    photo_2 = fields.Binary(
        "Photo 2",
        help="Add Photo",
        attachment=True,
    )
    photo_3 = fields.Binary(
        "Photo 3",
        help="Add Photo",
        attachment=True,
    )
    photo_4 = fields.Binary(
        "Photo 4",
        help="Add Photo",
        attachment=True,
    )
