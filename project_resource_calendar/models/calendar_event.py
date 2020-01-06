# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import babel.dates
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import time
from odoo.addons.calendar.models.calendar import Meeting
import pytz

VIRTUALID_DATETIME_FORMAT = '%Y%m%d%H%M%S'
ALL_DAY_DATE_FORMAT = '%Y-%m-%d'


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
    room_miscellaneous = fields.Many2many(
        string='Miscellaneous',
        related='room_id.miscellaneous',
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
    recurrency_icon = fields.Integer(
        compute='_compute_recurrency_icon'
    )
    is_cancelled = fields.Integer(
        compute='_compute_is_cancelled'
    )
    formated_start = fields.Datetime(
        compute='_compute_formated_date_for_report',
    )
    formated_stop = fields.Datetime(
        compute='_compute_formated_date_for_report',
    )

    def _compute_formated_date_for_report(self):
        self.formated_start = self._compute_formated(self.start_datetime)
        self.formated_stop = self._compute_formated(self.stop_datetime)

    def _compute_formated(self, date):
        formated_date = self.format_date(
            date,
            format_str='Y-MM-dd HH:mm:SS')
        return datetime.strptime(
            formated_date, '%Y-%m-%d %H:%M:%S')

    @api.one
    def _compute_recurrency_icon(self):
        self.ensure_one()
        if self.recurrency:
            self.recurrency_icon = 1
        else:
            self.recurrency_icon = 0

    @api.one
    def _compute_is_cancelled(self):
        self.ensure_one()
        if self.state == 'cancelled':
            self.is_cancelled = 1
        else:
            self.is_cancelled = 0

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
    @api.depends('start_datetime', 'allday', 'start_date')
    def _compute_get_weekday_number(self):
        if self.start_datetime and not self.allday:
            self.weekday_number = fields.Datetime\
                .context_timestamp(self, datetime
                                   .strptime(self.start_datetime,
                                             '%Y-%m-%d %H:%M:%S')).weekday()
        elif self.allday:
            self.weekday_number = datetime.strptime(
                self.start_date, '%Y-%m-%d').weekday()

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
            message = ''
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
            if record.recurrency and record.start and record.stop:
                record._compute_rrule()
                message = self._double_bookable_recurrent(record.id, room,
                                                          equipment, attendees,
                                                          message)
            else:
                events = self.env['calendar.event'].search([
                    ('id', '!=', record.id)])
                for event in events:
                    if self.is_event_overlaps_record(record, event):
                        message = self._get_resource_overlaps_message(
                            room, equipment, attendees, event, record, message)
            if message != '':
                raise ValidationError(
                    _(
                        'The following resources can not be double-booked:'
                        '\n %s',
                    ) % message,
                )

    @staticmethod
    def is_event_overlaps_record(record, event):
        return (event.start < record.stop) & (event.stop > record.start)

    @staticmethod
    def fill_validation_message(resource, start, stop):
        return _('%(resource)s: From: %(start)s To: %(stop)s\n') % {
            'resource': resource,
            'start': start,
            'stop': stop}

    @staticmethod
    def get_error_type(type_error):
        error_msg = ""
        if type_error == 'RESOURCE_TYPE_ERROR':
            error_msg = _('this resource is not bookable')
        if type_error == 'ROOM_TYPE_ERROR':
            error_msg = _('this room is not bookable')
        if type_error == 'TASK_CLONE_ERROR':
            error_msg = _(
                'This reservation can only be deleted from the Event module.')
        return error_msg

    def _double_bookable_recurrent(
            self, event_id, room, equipment, attendees, message):
        event = self.env['calendar.event'].browse(event_id)
        rec_dates = event._get_recurrent_dates_by_event()
        for rstart, rstop in rec_dates:
            rstart_str = rstart.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            rstop_str = rstop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            overlaps = self.env['calendar.event'].search([
                ('start', '<', rstop_str),
                ('stop', '>', rstart_str), ('id', '!=', event_id)])
            for overlap in overlaps:
                message += self._get_resource_overlaps_message(
                    room, equipment, attendees, overlap, event, message)
        return message

    def _get_resource_overlaps_message(self, room, equipment, attendees,
                                       overlap, event, message):
        if room:
            for resource in overlap.mapped(lambda s: s.room_id):
                if resource.id == event.room_id.id:
                    message += self.fill_validation_message(
                        resource.name,
                        self.format_date(overlap.start),
                        self.format_date(overlap.stop))
        if equipment:
            for resource in overlap.mapped(lambda s: s.equipment_ids):
                if resource.id in equipment.ids:
                    message += self.fill_validation_message(
                        resource.name,
                        self.format_date(overlap.start),
                        self.format_date(overlap.stop))
        if attendees:
            for resource in overlap.mapped(lambda s: s.partner_ids):
                if resource.id in attendees.ids:
                    message += self.fill_validation_message(
                        resource.name,
                        self.format_date(overlap.start),
                        self.format_date(overlap.stop))
        return message

    @api.multi
    @api.constrains('room_id', 'equipment_ids')
    def _check_resources_is_bookable(self):
        msg = ''
        for record in self:
            for equipment in record.equipment_ids:
                if not equipment.is_bookable:
                    msg += str(equipment.name) + ': ' + \
                        self.get_error_type('RESOURCE_TYPE_ERROR') + '\n'
            if record.room_id and not record.room_id.is_bookable:
                msg += str(record.room_id.name) + ': ' + \
                    self.get_error_type('ROOM_TYPE_ERROR') + '\n'
        if msg != '':
            raise ValidationError(msg)

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.equipment_ids = self.env['resource.calendar.instrument']\
                .search([('room_id', '=', self.room_id.id)])

    def format_date(self, date_to_format, format_str='dd-MMMM-yyyy HH:mm:ss'):
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
        return babel.dates.format_datetime(
            date_to_format,
            tzinfo=tz,
            format=format_str,
            locale=lang)

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
        formatted_date = self.format_date(date_to_format, 'EEEE dd MMMM yyyy')
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

    @staticmethod
    def room_in_user_groups(user, room):
        for group in user.groups_id:
            if group.room_ids and room.id in group.room_ids.ids:
                return True
        return False

    @api.multi
    def write(self, vals):
        self.validate_client_id_write(vals)
        current_user = self.env['res.users'].browse(self.env.uid)
        if self.create_uid.id != self.env.uid \
                and self.user_has_groups('project_resource_calendar'
                                         '.group_resource_calendar_editor') \
                and not self.user_has_groups('project_resource_calendar'
                                             '.group_resource'
                                             '_calendar_manager')\
                and current_user.partner_id.id not in self.partner_ids.ids\
                and self.room_id \
                and not self.room_in_user_groups(current_user, self.room_id):
            raise ValidationError(
                _('You are not allowed to do this operation, '
                  'please contact the system administrator'))
        return super(CalendarEvent, self).write(vals)

    @api.multi
    def validate_client_id_write(self, vals):
        for rec in self:
            if rec.is_task_event or (
                    'is_task_event' in vals and vals['is_task_event']):
                return
            if 'client_id' in vals:
                partners = rec.partner_ids.ids
                if 'partner_ids' in vals:
                    partners = vals['partner_ids'][0][2]
                    if not vals['client_id'] in partners:
                        vals['partner_ids'] = [
                            (6, 0, [vals['client_id']] +
                                vals['partner_ids'][0][2])]
                else:
                    if not vals['client_id'] in partners:
                        vals['partner_ids'] = [(4, vals['client_id'], 0)]
            elif 'partner_ids' in vals and rec.client_id.id not in \
                    vals['partner_ids'][0][2]:
                vals['partner_ids'] = [
                    (6, 0, vals['partner_ids'][0][2] + [rec.client_id.id])]

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

    def remove_recurrent_calendar_event(self, overlaps):
        overlaps_counter = len(overlaps.ids)
        for overlap in overlaps:
            if overlap.id == self.id:
                overlaps_counter -= 1
        return overlaps_counter

    def is_hr_resource_double_booked(self, attendee,
                                     date_start=None, date_end=None):
        if not date_end and not date_start:
            date_start = self.date_start
            date_end = self.date_end

        overlaps_partners = self.env['calendar.event'].search([
            ('partner_ids', 'in', attendee),
            ('start', '<', date_end),
            ('stop', '>', date_start),
            ('state', '!=', 'cancelled'),
        ])

        return self.remove_recurrent_calendar_event(overlaps_partners) > 0

    def get_double_booked_resources(self, date_start=None, date_end=None):
        booked_resources = []

        if not date_end and not date_start:
            date_start = self.start_datetime
            date_end = self.stop_datetime

        overlap_domain = [
            ('start', '<', date_end),
            ('stop', '>', date_start),
            ('state', '!=', 'cancelled')]

        if self.room_id:
            overlap_domain.append(('room_id', '=', self.room_id.id))
            overlaps = self.env['calendar.event'].search(overlap_domain)
            overlap_domain.remove(('room_id', '=', self.room_id.id))

            if self.remove_recurrent_calendar_event(overlaps) > 0:
                booked_resources.append(self.room_id.name)

        for equipment in self.equipment_ids:
            overlap_domain.append(('equipment_ids', 'in', equipment.id))
            overlaps_equipment = self.env['calendar.event']\
                .search(overlap_domain)

            if self.remove_recurrent_calendar_event(overlaps_equipment) > 0:
                booked_resources.append(equipment.name)

        for partner in self.partner_ids:
            if self.is_hr_resource_double_booked(partner.id,
                                                 date_start, date_end):
                booked_resources.append(partner.name)

        return booked_resources

    def get_calendar_booked_resources(self, room_id=None,
                                      equipment_ids=None,
                                      partner_ids=None,
                                      date_start=None,
                                      duration=None, allday=False):
        if allday:
            date_end = (datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S') +
                        timedelta(hours=23, minutes=59)).strftime(
                '%Y-%m-%d %H:%M:%S')
        else:
            date_end = (datetime.strptime(
                date_start, '%Y-%m-%d %H:%M:%S') + timedelta(
                hours=duration)).strftime('%Y-%m-%d %H:%M:%S')

        booked_resources = []
        overlap_domain = [
            ('start', '<', date_end),
            ('stop', '>', date_start),
            ('state', '!=', 'cancelled')]

        if room_id:
            overlap_domain.append(('room_id', '=', room_id))
            overlaps = self.env['calendar.event'].search(overlap_domain)
            overlap_domain.remove(('room_id', '=', room_id))

            if self.remove_recurrent_calendar_event(overlaps) > 0:
                booked_resources.append(self.env['resource.calendar.room']
                                        .browse(room_id).name)

        for equipment in equipment_ids:
            overlap_domain.append(('equipment_ids', 'in', equipment))
            overlaps_equipment = self.env['calendar.event']\
                .search(overlap_domain)

            if self.remove_recurrent_calendar_event(overlaps_equipment) > 0:
                booked_resources.append(self
                                        .env['resource.calendar.instrument']
                                        .browse(equipment).name)

        for partner in partner_ids:
            if self.is_hr_resource_double_booked(partner,
                                                 date_start, date_end):
                booked_resources.append(self.env['res.partner']
                                        .browse(partner).name)

        return booked_resources

    @api.model
    def search_read(
            self, domain=None, fields=None, offset=0,
            limit=None, order=None):
        if domain and domain[0] and domain[0][0] and domain[0][0] == 'start':
            week_diff = timedelta(-7, 1)
            domain_interval = datetime.strptime(
                domain[1][2], '%Y-%m-%d %H:%M:%S') - datetime.strptime(
                domain[0][2], '%Y-%m-%d %H:%M:%S')
            if domain[0][2][-8:] == '23:59:59'\
                    and domain_interval == week_diff:
                tz = self.env['res.users'].browse(self.env.uid).tz or 'utc'
                my_timestamp = datetime.strptime(
                    domain[0][2], '%Y-%m-%d %H:%M:%S')
                my_tz = pytz.timezone(tz)
                utc_tz = pytz.timezone('utc')
                time_in_utc_tz = my_tz.localize(my_timestamp).astimezone(
                    utc_tz).strftime("%Y-%m-%d %H:%M:%S")
                domain[0][2] = time_in_utc_tz
        res = super(CalendarEvent, self).search_read(
            domain,
            fields,
            offset,
            limit,
            order)
        return res

    @api.multi
    def action_detach_recurring_event(self):
        meeting = self.detach_recurring_event()
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'res_id': meeting.id,
            'target': 'main',
            'context': context,
        }

    def get_real_ids(self, ids):
        if isinstance(ids, (pycompat.string_types, pycompat.integer_types)):
            return self.calendar_id2real_id(ids)

        if isinstance(ids, (list, tuple)):
            return [self.calendar_id2real_id(_id) for _id in ids]

    @api.multi
    def export_data(self, fields_to_export, raw_data=False):
        """ Override to convert virtual ids to ids """
        records = self.browse(set(self.get_real_ids(self.ids)))

        real_records = []
        virtual_data = []
        for record in records:
            if isinstance(record.ids[0], int):
                real_records.append(record.ids[0])
                virtual_data.append(False)
            else:
                real_records.append(record.ids[0][0])
                virtual_data.append((record.ids[0][1], record.ids[0][2]))
        return super(
            Meeting,
            self.browse(real_records)).export_data(
            fields_to_export,
            raw_data,
            virtual_data)

    def calendar_id2real_id(self, calendar_id=None, with_date=True):
        """ Convert a "virtual/recurring event id" (type string)
        into a real event id (type int).
            E.g. virtual/recurring event id is 4-20091201100000,
            so it will return 4.
            :param calendar_id: id of calendar
            :param with_date: if a value is passed to this param it will
            return dates based on value of withdate + calendar_id
            :return: real event id
        """
        if calendar_id and isinstance(calendar_id, pycompat.string_types):
            res = [bit for bit in calendar_id.split('-') if bit]
            if len(res) == 2:
                real_id = res[0]
                if self.browse(real_id).allday:
                    r_start = datetime.strptime(
                        self.browse(real_id).start_date,
                        ALL_DAY_DATE_FORMAT)
                    r_stop = datetime.strptime(
                        self.browse(real_id).stop_date,
                        ALL_DAY_DATE_FORMAT)
                    delta = r_stop - r_start
                    real_date = fields.Datetime.context_timestamp(
                        self,
                        datetime.strptime(
                            time.strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT,
                                time.strptime(
                                    res[1],
                                    VIRTUALID_DATETIME_FORMAT)),
                            '%Y-%m-%d %H:%M:%S')) .strftime(ALL_DAY_DATE_FORMAT)
                    start = datetime.strptime(real_date, ALL_DAY_DATE_FORMAT)
                    end = (start + delta).strftime(ALL_DAY_DATE_FORMAT)
                    return (
                        int(real_id),
                        real_date + ' 00:00:00',
                        end + ' 23:59:59')
                elif with_date:
                    r_start = datetime.strptime(
                        self.browse(real_id).start_datetime,
                        DEFAULT_SERVER_DATETIME_FORMAT)
                    r_stop = datetime.strptime(
                        self.browse(real_id).stop_datetime,
                        DEFAULT_SERVER_DATETIME_FORMAT)
                    delta = r_stop - r_start
                    real_date = fields.Datetime.context_timestamp(
                        self,
                        datetime.strptime(
                            time.strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT,
                                time.strptime(
                                    res[1],
                                    VIRTUALID_DATETIME_FORMAT)),
                            '%Y-%m-%d %H:%M:%S')) .strftime('%Y-%m-%d %H:%M:%S')
                    start = datetime.strptime(
                        real_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    end = (
                        start + delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    return (int(real_id), real_date, end)
                return int(real_id)
        return calendar_id and int(calendar_id) or calendar_id
