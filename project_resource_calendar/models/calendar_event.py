# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import babel.dates
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
    room_floor = fields.Char(
        string='Floor',
        related='room_id.floor',
    )
    allow_room_double_booking = fields.Boolean(
        string='Allow double book',
        related='room_id.allow_double_book',
    )
    equipment_ids = fields.Many2many(
        string='Equipment',
        comodel_name='resource.calendar.instrument',
        ondelete='set null',
    )
    double_bookable_equipment_ids = fields.Many2many(
        string='Double bookable equipments',
        compute='_get_double_bookable_equipments',
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
        compute="_compute_get_weekday_number"
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
        compute='_compute_calculate_recurrent'
    )
    recurrence_type = fields.Char(
        string='Recurrence Type',
        compute='_compute_calculate_recurrence_type'
    )

    client_id_partner_ids_names = fields.Char(
        compute='_compute_get_client_id_partner_ids_names'
    )
    client_id = fields.Many2one(
        'res.partner',
        string='Client',
        readonly=False,
    )
    user_id = fields.Many2one(string='Responsible User')
    partner_id = fields.Many2one(string='Responsible Partner')
    partner_ids = fields.Many2many(
        'res.partner',
        'calendar_event_res_partner_rel',
        string='Attendees',
        states={'done': [('readonly', True)]},
        default=None)
    current_id = fields.Char(
        'Current ID',
    )

    @api.one
    @api.depends('room_id')
    def _get_double_bookable_equipments(self):
        double_bookable_equipment_ids = []
        for equipment in self.equipment_ids:
            if equipment.allow_double_book:
                double_bookable_equipment_ids.append(equipment.id)
        self.double_bookable_equipment_ids = double_bookable_equipment_ids

    @api.onchange('client_id')
    def _onchange_client_id(self):
        if not self.is_task_event and self.client_id:
            self.partner_ids = [(6, 0,
                                 [self.client_id.id] + self.partner_ids.ids)]

    def _compute_calculate_recurrent(self):
        if self.recurrency:
            self.recurrent_state = _("Yes")
        else:
            self.recurrent_state = _("No")

    def _compute_calculate_recurrence_type(self):
        if self.recurrency:
            recurrence_frequency = {
                'daily': _('Day(s)'),
                'weekly': _('Week(s)'),
                'monthly': _('Month(s)'),
                'yearly': _('Year(s)')
            }
            if self.end_type == 'end_date':
                self.recurrence_type = str(self.interval) + _(" Time(s) ") + \
                    _(recurrence_frequency[self.rrule_type]) + _(" until ") + \
                    self.final_date
            else:
                self.recurrence_type = str(self.interval) + _(" Time(s) ") + \
                    _(recurrence_frequency[self.rrule_type]) + _(" for ") + \
                    str(self.count) + _(" Time(s)")

    def _get_res_partners_names(self):
        return str(list(map(lambda partner:
                            str(partner.name),
                            self.partner_ids))) \
            .replace('[', '').replace(']', '').replace("'", "")

    @api.one
    def _compute_get_client_id_partner_ids_names(self):
        if self.is_task_event:
            self.client_id_partner_ids_names = self.client_id.name
        else:
            self.client_id_partner_ids_names = self._get_res_partners_names()

    @api.one
    @api.depends('start_datetime')
    def _compute_get_weekday_number(self):
        if self.start_datetime:
            self.weekday_number = datetime.strptime(
                self.start_datetime, '%Y-%m-%d %H:%M:%S'
            ).weekday()

    @api.constrains('interval')
    def _check_interval_greater_than_0(self):
        for record in self:
            if record.interval < 1:
                raise ValidationError(_('The interval must be greater than 0'))

    @api.constrains('count')
    def _check_count_greater_than_0(self):
        for record in self:
            if record.count < 1:
                raise ValidationError(
                    _('The number of repetitions must be greater than 0'))

    @api.multi
    @api.constrains('room_id', 'start', 'stop', 'equipment_ids', 'partner_ids')
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
            attendees = record.partner_ids.filtered(
                lambda s: s.allow_double_book is False
            )
            if not room and not equipment and not attendees:
                continue
            events = self.env['calendar.event'].search([
                ('id', '!=', record.id),
            ])
            for event in events:
                if self.is_event_overlaps_record(record, event):
                    for resource in event.mapped(lambda s: s.room_id):
                        if resource.id == record.room_id.id:
                            raise ValidationError(
                                _(
                                    'The room %s cannot be double-booked '
                                    'with any overlapping meetings or events.',
                                ) % resource.name,
                            )
                    for resource in event.mapped(lambda s: s.equipment_ids):
                        if resource.id in record.equipment_ids.ids:
                            raise ValidationError(
                                _(
                                    'The resource %s cannot be double-booked '
                                    'with any overlapping meetings or events.',
                                ) % resource.name,
                            )
                    for resource in event.mapped(lambda s: s.partner_ids):
                        if resource.id in record.partner_ids.ids:
                            raise ValidationError(
                                _(
                                    'The attendee %s cannot be double-booked '
                                    'with any overlapping meetings or events.',
                                ) % resource.name,
                            )

    @staticmethod
    def is_event_overlaps_record(record, event):
        return (event.start < record.stop) & (event.stop > record.start)

    def get_error_type(self, type_error):
        error_msg = ""
        if type_error == 'RESOURCE_TYPE_ERROR':
            error_msg = _('this resource is not bookable')
        if type_error == 'ROOM_TYPE_ERROR':
            error_msg = _('this room is not bookable')
        if type_error == 'TASK_CLONE_ERROR':
            error_msg = _(
                'This reservation can only be deleted from the Event module.')
        return error_msg

    @api.multi
    @api.constrains('room_id', 'equipment_ids')
    def _check_resources_is_bookable(self):
        for record in self:
            for equipment in record.equipment_ids:
                if not equipment.is_bookable:
                    raise ValidationError(str(equipment.name)
                                          + ': ' + self.get_error_type(
                                              'RESOURCE_TYPE_ERROR'))

            if record.room_id and not record.room_id.is_bookable:
                raise ValidationError(str(record.room_id.name)
                                      + ': ' + self.get_error_type(
                                          'ROOM_TYPE_ERROR'))

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.equipment_ids = self.env['resource.calendar.instrument']\
                .search([('room_id', '=', self.room_id.id)])

    def get_formatted_date(self, date_to_format, field_name, format):
        recurrent = None
        if self.recurrency:
            recurrent = self.env['calendar.event'].browse(self.current_id)
        if format:
            if field_name == 'start_date':
                if recurrent:
                    date_to_format = recurrent.start_date
                else:
                    date_to_format = self.start_date
            elif field_name == 'start_datetime':
                if recurrent:
                    date_to_format = recurrent.start_datetime
                else:
                    date_to_format = self.start_datetime
        lang = self.env['res.users'].browse(self.env.uid).lang or 'en_US'
        tz = self.env['res.users'].browse(self.env.uid).tz or 'utc'
        if not isinstance(date_to_format, datetime):
            if self.allday:
                date_to_format = datetime.strptime(
                    date_to_format, '%Y-%m-%d'
                )
            else:
                date_to_format = datetime.strptime(
                    date_to_format, '%Y-%m-%d %H:%M:%S'
                )
        formatted_date = babel.dates.format_datetime(
            date_to_format,
            tzinfo=tz,
            format='EEEE dd MMMM yyyy',
            locale=lang)
        return formatted_date.capitalize()

    def print_calendar_report(self):
        return self.env.ref(
            'project_resource_calendar.calendar_event_report'

        ).report_action(self)

    @api.model
    def create(self, vals):
        self.verify_client_in_participants(vals)
        return super(CalendarEvent, self).create(vals)

    @staticmethod
    def verify_client_in_participants(vals):
        if 'is_task_event' in vals and vals['is_task_event']:
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
        if self.is_task_event or (
                'is_task_event' in vals and vals['is_task_event']):
            return
        if 'client_id' in vals:
            partners = self.partner_ids.ids
            if 'partner_ids' in vals:
                partners = vals['partner_ids'][0][2]
                if not vals['client_id'] in partners:
                    vals['partner_ids'] = [
                        (6, 0, [vals['client_id']] +
                            vals['partner_ids'][0][2])]
            else:
                if not vals['client_id'] in partners:
                    vals['partner_ids'] = [(4, vals['client_id'], 0)]
        else:
            if (
                'partner_ids' in vals and
                    self.client_id.id not in vals['partner_ids'][0][2]):
                vals['partner_ids'] = [
                    (6, 0, vals['partner_ids'][0][2] + [self.client_id.id])]

    @api.multi
    def unlink(self):
        for record in self:
            if record.event_task_id:
                raise ValidationError(
                    _(
                        self.get_error_type('TASK_CLONE_ERROR')
                    )
                )
        return super(CalendarEvent, self).unlink()
