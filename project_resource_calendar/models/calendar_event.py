# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CalendarEvent(models.Model):

    _inherit = 'calendar.event'

    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equipment'),
        ('room', 'Room')],
        string='Resource Type',
        default='room',
    )
    room_id = fields.Many2one(
        string='Room',
        comodel_name='resource.calendar.room',
        ondelete='set null',
    )
    equipment_ids = fields.Many2many(
        string='Equipment',
        comodel_name='resource.calendar.instrument',
        ondelete='set null',
    )
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('open', 'Confirmed'),
        ('cancelled', 'Cancelled')],
        string='Status',
        readonly=True,
        track_visibility='onchange',
        default='draft')

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_open(self):
        self.write({'state': 'open'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.multi
    @api.constrains('room_id', 'start', 'stop', 'equipment_ids')
    def _check_room_id_double_book(self):

        for record in self:

            if record._event_in_past() or record.state == 'draft':
                continue

            room = record.room_id.filtered(
                lambda s: s.allow_double_book is False
            )
            equipment = record.equipment_ids.filtered(
                lambda s: s.allow_double_book is False
            )

            if not any(room) and not any(equipment):
                continue

            overlaps = self.env['calendar.event'].search([
                ('id', '!=', record.id),
                ('start', '<', record.stop),
                ('stop', '>', record.start),
            ])

            for resource in overlaps.mapped(lambda s: s.room_id):
                raise ValidationError(
                    _(
                        'The room cannot be double-booked '
                        'with any overlapping meetings or events.',
                    )
                )
            for resource in overlaps.mapped(lambda s: s.equipment_ids):
                raise ValidationError(
                    _(
                        'The resource cannot be double-booked '
                        'with any overlapping meetings or events.',
                    )
                )
