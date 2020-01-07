# Copyright 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class Resource(models.Model):
    _inherit = 'resource.resource'

    name = fields.Char(
        required=True,
        string='Name',
    )
    resource_type = fields.Selection(
        [('user', 'Human'),
         ('material', 'Material'),
         ('room', 'Room')],
        string='Resource Type',
        default='user',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )
    is_bookable = fields.Boolean(
        string='Is Bookable',
        default=True,
    )
    group_ids = fields.Many2many(
        'res.groups',
        string='Group',
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
    pricing = fields.Float(
        string='Pricing ($)',
    )
    pricing_type = fields.Selection(
        [('fixed', 'Fixed Rate'),
         ('hour', 'Per Hour')],
        string='Pricing Type',
        default='fixed',
    )
    allow_double_book = fields.Boolean(
        string='Allow Double Booking',
        help='Check if this resource '
             'can be booked in more than '
             'one meeting or event at the same '
             'time.',
        default=True,
    )

    @api.onchange('is_bookable')
    def _compute_allow_double_book(self):
        if not self.is_bookable:
            self.allow_double_book = False

    @api.model
    def write(self, vals):
        if 'is_bookable' in vals and vals['is_bookable'] is False:
            vals['allow_double_book'] = False
        return super().write(vals)

    @api.model
    def create(self, vals):
        if 'is_bookable' in vals and vals['is_bookable'] is False:
            vals['allow_double_book'] = False
        return super().create(vals)
