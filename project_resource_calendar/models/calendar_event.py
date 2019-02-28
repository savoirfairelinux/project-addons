# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


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
        default='open')
    weekday_number = fields.Integer(
        string='Weekday number',
        compute="_get_weekday_number"
    )
    event_task_id = fields.Many2one(
        string='Task',
        comodel_name='project.task',
        ondelete='set null',
    )
    is_task_event = fields.Boolean(
        string='Is Created From Task',
        default=False,
    )
    start_datetime = fields.Datetime(
        'Start DateTime',
        compute='_compute_dates',
        inverse='_inverse_dates',
        store=True,
        states={
            'done': [
                ('readonly', [
                    ('id', '!=', False),
                    ('recurrency', '=', True),
                    ('is_task_event', '=', True)])]
        },
        track_visibility='onchange',
    )
    stop_datetime = fields.Datetime(
        'End Datetime',
        compute='_compute_dates',
        inverse='_inverse_dates',
        store=True,
        states={'done': [('readonly',
                          [('id', '!=', False),
                           ('recurrency', '=', True),
                           ('is_task_event', '=', True)]
                          )]},
        track_visibility='onchange',
    )
    duration = fields.Float(
        'Duration',
        states={'done': [('readonly',
                          [('id', '!=', False),
                           ('recurrency', '=', True),
                           ('is_task_event', '=', True)]
                          )]}
    )
    recurrent_state = fields.Char(
        string='Recurring',
        compute='_calculate_recurrent'
    )
    recurrence_type = fields.Char(
        string='Recurrence Type',
        compute='_calculate_recurrence_type'
    )

    partner_ids_names = fields.Char(
        compute='_get_res_partners_names'
    )
    client_id = fields.Many2one(
        'res.partner',
        string='Client',
        readonly=False,
        required=True,
    )
    user_id = fields.Many2one(string='Responsible User')
    partner_id = fields.Many2one(string='Responsible Partner')
    partner_ids = fields.Many2many(
        'res.partner',
        'calendar_event_res_partner_rel',
        string='Attendees',
        states={'done': [('readonly', True)]},
        default=None)

    @api.onchange('client_id')
    def _add_client_to_participants(self):
        if not self.is_task_event and self.client_id:
            self.partner_ids = [(6, 0,
                                 [self.client_id.id] + self.partner_ids.ids)]

    def _calculate_recurrent(self):
        if self.recurrency:
            self.recurrent_state = _("Yes")
        else:
            self.recurrent_state = _("No")

    def _calculate_recurrence_type(self):
        if self.recurrency:
            if self.end_type == 'end_date':
                self.recurrence_type = str(self.interval) + _(" Time(s)") + \
                    str(self.rrule_type) + _(" until ") + \
                    self.final_date
            else:
                self.recurrence_type = str(self.interval) + _(" Time(s) ") + \
                    str(self.rrule_type) + _(" for ") + \
                    str(self.count) + _(" Time(s)")

    @api.one
    def _get_res_partners_names(self):
        if self.is_task_event:
            self.partner_ids_names = self.partner_id.name
        else:
            self.partner_ids_names = str(list(map(lambda partner:
                                                  str(partner.name),
                                                  self.partner_ids)))\
                .replace('[', '').replace(']', '').replace("'", "")

    @api.one
    @api.depends('start_datetime')
    def _get_weekday_number(self):
        if self.start_datetime:
            self.weekday_number = datetime.strptime(
                self.start_datetime, '%Y-%m-%d %H:%M:%S'
            ).weekday()

    @api.multi
    @api.constrains('room_id', 'start', 'stop', 'equipment_ids')
    def _check_resources_double_book(self):
        for record in self:
            if record._event_in_past() or record.state == 'cancelled':
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
                if resource.id == record.room_id.id:
                    raise ValidationError(
                        _(
                            'The room, %s,  cannot be double-booked '
                            'with any overlapping meetings or events.',
                        ) % resource.name,
                    )
            for resource in overlaps.mapped(lambda s: s.equipment_ids):
                if resource.id in record.equipment_ids.ids:
                    raise ValidationError(
                        _(
                            'The resource, %s, cannot be double-booked '
                            'with any overlapping meetings or events.',
                        ) % resource.name,
                    )

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.equipment_ids = self.env['resource.calendar.instrument']\
                .search([('room_id', '=', self.room_id.id)])

    def print_calendar_report(self):
        return self.env.ref(
            'project_resource_calendar.calendar_event_report'
        ).report_action(self)

    @api.model
    def create(self, vals):
        self.verify_client_in_participants(vals)
        return super(CalendarEvent, self).create(vals)

    def verify_client_in_participants(self, vals):
        if self.is_task_event:
            return
        if 'client_id' in vals and vals['client_id']:
            if not vals['client_id'] in vals['partner_ids'][0][2]:
                vals['partner_ids'] = [
                    (6, 0, vals['partner_ids'][0][2] + [vals['client_id']])]

    @api.multi
    def write(self, vals):
        self.validate_client_id_write(vals)
        return super(CalendarEvent, self).write(vals)

    def validate_client_id_write(self, vals):
        if self.is_task_event:
            return
        if 'client_id' in vals:
            partners = self.partner_ids.ids
            if 'partner_ids' in vals:
                partners = vals['partner_ids'][0][2]
                if not vals['client_id'] in partners:
                    vals['partner_ids'] = [
                        (6, 0, [vals['client_id']] + vals['partner_ids'][0][2])]
            else:
                if not vals['client_id'] in partners:
                    vals['partner_ids'] = [(4, vals['client_id'], 0)]
        else:
            if 'partner_ids' in vals and self.client_id.id not in vals['partner_ids'][0][2]:
                vals['partner_ids'] = [
                    (6, 0, vals['partner_ids'][0][2] + [self.client_id.id])]
