# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class Task(models.Model):
    _inherit = ['project.task']
    _name = 'project.task'

    resource_type = fields.Selection([
        ('user', 'Human'),
        ('material', 'Material')],
        string='Resource Type',
        default='material',
    )
   
    resource_ids = fields.Many2many(
        string='Resources',
        comodel_name='resource.resource',
    )
    start = fields.Datetime('Start', help="Start date of an event, without time for full days events")
    stop = fields.Datetime('Stop', help="Stop date of an event, without time for full days events")

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id.is_reservation_trigger:
            self.do_reservation()
        import ipdb; ipdb.set_trace()
    
    def do_reservation(self):
        if self.resource_ids and self.start and self.stop:
            self.env['calendar.event'].create({
                'name': self.name,
                'start': self.start,
                'stop': self.stop
            })
    # room_id = fields.Many2one(
    #     string='Room',
    #     comodel_name='resource.calendar.room',
    #     ondelete='set null',
    #     track_visibility='onchange',
    # )
    # equipment_id = fields.Many2one(
    #     string='Equipment',
    #     comodel_name='resource.calendar.instrument',
    #     ondelete='set null',
    #     track_visibility='onchange',
    # )

    # @api.model
    # def create(self, vals):
    #     if self.is_new_activity(vals):
    #         return self.create_activity(vals)
    #     elif self.is_new_task(vals):
    #         return self.create_task(vals)
    #     else:
    #         return super(Task, self).create(vals)

    # @api.multi
    # def write(self, vals):
    #     if self.is_activity():
    #         return self.write_activity(vals)
    #     else:
    #         self.update_reservation_event(vals)
    #         if 'employee_ids' in vals:
    #             self.message_unsubscribe(list(
    #                 self.get_partners()))
    #             if vals['employee_ids'][0][2]:
    #                 self.message_subscribe(list(self.get_partners(
    #                     vals['employee_ids'][0][2])), force=False)
    #             else:
    #                 self.message_subscribe(list([]), force=False)

    #         return super(Task, self).write(vals)

    # @api.multi
    # def copy(self, default=None):
    #     if default is None:
    #         default = {}
    #     if not default.get('name'):
    #         default['name'] = _("%s (copy)") % self.name
    #     if 'remaining_hours' not in default:
    #         default['remaining_hours'] = self.planned_hours
    #     default['task_state'] = 'draft'
    #     default['reservation_event_id'] = False
    #     new_copy = super(Task, self).copy(default)
    #     if self.is_activity():
    #         child_default_vals = {'parent_id': new_copy.id}
    #         for child in self.child_ids:
    #             if 'name' in child_default_vals:
    #                 child_default_vals.pop('name')
    #             if child.is_main_task:
    #                 continue
    #             child.copy(default=child_default_vals)
    #     return new_copy

    # @api.onchange('resource_type')
    # def _onchange_resource_type(self):
    #     self.room_id = None
    #     self.equipment_id = None

    # @api.onchange('room_id')
    # def _onchange_room_id(self):
    #     self.verify_room_bookable()

    # @api.onchange('equipment_id')
    # def _onchange_equipment_id(self):
    #     self.verify_equipment_bookable()

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     self._onchange_partner_id()
    #     if self.partner_id:
    #         self.client_type = self.partner_id.tag_id.client_type

    # def verify_room_bookable(self):
    #     if self.room_id:
    #         if not self.room_id.is_bookable:
    #             raise ValidationError(str(self.room_id.name) + ': ' +
    #                                   self.get_error_type('ROOM_TYPE_ERROR'))

    # def verify_equipment_bookable(self):
    #     if self.equipment_id:
    #         if not self.equipment_id.is_bookable:
    #             raise ValidationError(str(self.equipment_id.name) + ': ' +
    #                                   self.get_error_type(
    #                                       'RESOURCE_TYPE_ERROR'))

    # @api.multi
    # def update_reservation_event(self, vals):
    #     if len(self) == 1:
    #         if self.reservation_event_id:
    #             reservation_event = self.env['calendar.event']. \
    #                 browse(self.reservation_event_id)
    #             field_names = [
    #                 'date_start', 'date_end', 'equipment_id',
    #                 'name', 'resource_type', 'room_id', 'client_type',
    #                 'employee_ids', 'sector_id', 'category_id', 'partner_id',
    #             ]
    #             reservation_event.write(
    #                 self.set_value_reservation_event(field_names, vals)
    #             )

    # def set_value_reservation_event(self, field_names, vals):
    #     update_vals = {}
    #     for index in range(0, len(field_names)):
    #         if field_names[index] in vals:
    #             if field_names[index] == 'partner_id':
    #                 update_vals['client_id'] = vals[field_names[index]]
    #             if field_names[index] == 'date_start':
    #                 update_vals['start'] = vals[field_names[index]]
    #             if field_names[index] == 'date_end':
    #                 update_vals['stop'] = vals[field_names[index]]
    #             if field_names[index] == 'equipment_id' \
    #                     and vals['equipment_id']:
    #                 update_vals.update(self.update_value_equipment_id(vals))
    #             elif field_names[index] == 'room_id':
    #                 if vals['room_id']:
    #                     update_vals.update(self.update_value_room_id(vals))
    #                 update_vals[field_names[index]] = vals[field_names[index]]
    #             if field_names[index] == 'employee_ids':
    #                 update_vals['partners_ids'] = self\
    #                     .get_partners()
    #                 update_vals.update(self.update_value_employee_ids(vals))
    #             if field_names[index] in ('sector_id',
    #                                       'category_id',
    #                                       'resource_type',
    #                                       'name',
    #                                       'client_type'):
    #                 update_vals[field_names[index]] = vals[field_names[index]]
    #     return update_vals

    # @staticmethod
    # def update_value_equipment_id(vals):
    #     set_value = {}
    #     set_value['equipment_ids'] = \
    #         [(6, 0, [vals['equipment_id']])]
    #     set_value['room_id'] = False
    #     return set_value

    # def update_value_room_id(self, vals):
    #     set_value = {}
    #     set_value['equipment_ids'] = \
    #         [(6, 0, self.env['resource.calendar.room'].
    #           browse(vals['room_id']).instruments_ids.ids)]
    #     return set_value

    # def update_value_employee_ids(self, vals):
    #     set_value = {}
    #     set_value['partner_ids'] = [(
    #         6, 0, self.get_updated_partners(
    #             vals['employee_ids'][0][2]))]
    #     return set_value

    # @api.multi
    # @api.depends('name', 'code')
    # def name_get(self):
    #     result = []
    #     for task in self:
    #         if task.is_type_task():
    #             name = task.code + '/' + task.name
    #         else:
    #             name = task.name
    #         result.append((task.id, name))
    #     return result

    # @staticmethod
    # def get_task_order(task_ds, activity_ds, format):
    #     time_diff = datetime.strptime(task_ds, format) \
    #         - datetime.strptime(activity_ds, format)
    #     return time_diff.days * HOURS_IN_DAY * MINUTES_IN_HOUR \
    #         + time_diff.seconds / CONVERT_SECONDS_TO_MINUTE

    # def action_done(self):
    #     self.open_resources_reservation()
    #     self.write({'task_state': 'done'})
    #     self.send_message('done')

    # @api.multi
    # def action_request(self):
    #     return self.get_confirmation_wizard('request')

    # @api.multi
    # def action_option(self):
    #     return self.get_confirmation_wizard('option')

    # @api.multi
    # def action_return_option(self):
    #     self.write({'task_state': 'option'})
    #     if self.is_activity():
    #         for child in self.child_ids:
    #             child.write({'task_state': 'option'})
    #             child.do_clone_task_reservation()
    #             child.send_message('option')
    #     else:
    #         self.do_clone_task_reservation()
    #         self.send_message('option')

    # def get_booked_resources(self):
    #     res = ''
    #     if self.is_type_task() and self.is_resource_booked():
    #         res += self.room_id.name + '<br>' if (
    #             self.room_id) else self.equipment_id.name + '<br>'
    #     for attendee in self.get_partners():
    #         hres = self.is_hr_resource_double_booked(attendee)
    #         partner_attendee = self.env['res.partner'].browse(attendee)
    #         if hres and partner_attendee:
    #             res += partner_attendee.name + '<br>'
    #     if self.is_activity():
    #         for child in self.child_ids:
    #             if child.is_resource_booked():
    #                 res += child.room_id.name + \
    #                     ' - ' + child.date_start + \
    #                     ' - ' + child.date_end + \
    #                     ' - ' + child.code + \
    #                     '<br>' if child.room_id else (
    #                         child.equipment_id.name + ' - ' +
    #                         child.date_start + ' - ' + child.date_end +
    #                         ' - ' + child.code + '<br>')
    #             for attendee in child.get_partners():
    #                 hres = child.is_hr_resource_double_booked(attendee)
    #                 attendee_partner = self.env['res.partner'].browse(attendee)
    #                 if hres and attendee_partner:
    #                     res += attendee_partner.name + \
    #                         ' - ' + child.date_start + \
    #                         ' - ' + child.date_end + \
    #                         ' - ' + child.code + \
    #                         '<br>'
    #     return res

    # def get_double_booked_resources(self, room_id=None,
    #                                 equipment_id=None,
    #                                 employee_ids=None,
    #                                 date_start=None, date_end=None):

    #     booked_resources = []
    #     if not date_end and not date_start:
    #         date_start = self.date_start
    #         date_end = self.date_end

    #     if not room_id:
    #         room_id = self.room_id.id

    #     if not equipment_id:
    #         equipment_id = self.equipment_id.id

    #     if not employee_ids:
    #         partner_ids = self.get_partners()
    #     else:
    #         partner_ids = self.get_partners(employee_ids)

    #     if self.room_id:
    #         overlaps = self.env['calendar.event'].search([
    #             ('room_id', '=', room_id),
    #             ('start', '<', date_end),
    #             ('stop', '>', date_start),
    #             ('state', '!=', 'cancelled'),
    #         ])
    #         overlaps_ids = overlaps.ids
    #         for overlap_id in overlaps_ids:
    #             if self.env['calendar.event']\
    #                     .browse(overlap_id).event_task_id.id == self.id:
    #                 overlaps_ids.remove(overlap_id)
    #         if len(overlaps_ids) > 0:
    #             booked_resources.append(self.env['resource.calendar.room']
    #                                     .browse(room_id).name)

    #     overlaps_equipment = self.env['calendar.event'].search([
    #         ('equipment_ids', 'in', [equipment_id]),
    #         ('start', '<', date_end),
    #         ('stop', '>', date_start),
    #         ('state', '!=', 'cancelled'),
    #     ])
    #     overlaps_equipment_ids = overlaps_equipment.ids
    #     for overlap_equipment_id in overlaps_equipment_ids:
    #         if self.env['calendar.event']\
    #                 .browse(overlap_equipment_id)\
    #                 .event_task_id.id == self.id:
    #             overlaps_equipment_ids.remove(overlap_equipment_id)
    #     if len(overlaps_equipment_ids) > 0:
    #         booked_resources.append(self.env['resource.calendar.instrument']
    #                                     .browse(equipment_id).name)

    #     for attendee in partner_ids:
    #         h_res = self.is_hr_resource_double_booked(attendee)
    #         partner_attendee = self.env['res.partner'].browse(attendee)
    #         if h_res and partner_attendee:
    #             booked_resources.append(partner_attendee.name)

    #     return booked_resources

    # @api.multi
    # def get_partners(self, employee_ids=None):
    #     if not employee_ids:
    #         employees = self.employee_ids
    #     else:
    #         employees = self.env['hr.employee']\
    #             .search([('id', 'in', employee_ids)])
    #     partners = []
    #     for e in employees:
    #         if e.user_id:
    #             partners.append(e.user_id.partner_id.id)
    #     return partners

    # @api.multi
    # def get_updated_partners(self, employee_ids):
    #     partner_ids = []
    #     employee = self.env['hr.employee']
    #     for e in employee_ids:
    #         emp = employee.browse(e)
    #         if emp.user_id:
    #             partner_ids.append(emp.user_id.partner_id.id)
    #     return partner_ids

    # @api.multi
    # def request_reservation(self):
    #     self.ensure_one()
    #     calendar_event = self.env['calendar.event']
    #     values = {
    #         'start': self.date_start,
    #         'stop': self.date_end,
    #         'name': self.complete_name,
    #         'resource_type': self.resource_type,
    #         'room_id': self.room_id.id if self.room_id else None,
    #         'equipment_ids': [(
    #             4, self.equipment_id.id, 0)] if self.equipment_id else None,
    #         'partner_ids': [(6, 0, self.get_partners())],
    #         'client_id': self.partner_id.id,
    #         'client_type': self.client_type.id,
    #         'state': 'open',
    #         'event_task_id': self.id,
    #         'is_task_event': True,
    #         'sector_id': self.sector_id.id if self.sector_id else None,
    #         'category_id': self.category_id.id,
    #     }
    #     new_event = calendar_event.create(values)
    #     self.reservation_event_id = new_event.id
    #     if self.room_id:
    #         self.reserve_equipment_inside(new_event.id)

    # def get_calendar_event(self):
    #     self.ensure_one()
    #     return self.env['calendar.event'].search(
    #         [('event_task_id', '=', self.id)])

    # @api.multi
    # def reserve_equipment_inside(self, event_id):
    #     self.ensure_one()
    #     calendar_event = self.env['calendar.event'].browse(event_id)
    #     calendar_event.write(
    #         {
    #             'equipment_ids': [(6, 0, self.get_equipment_ids_inside())]
    #         })

    # @api.multi
    # def get_equipment_ids_inside(self):
    #     room_id = self.env['resource.calendar.room']. \
    #         browse(self.room_id).id
    #     return room_id.instruments_ids.ids

    # @api.multi
    # def cancel_resources_reservation(self):
    #     self.ensure_one()
    #     if self.reservation_event_id:
    #         reserve_event = self.info_calendar_event()
    #         reserve_event.write(
    #             {'state': 'cancelled'}
    #         )
    #         reserve_event.event_task_id = False

    # @api.multi
    # def draft_resources_reservation(self):
    #     self.ensure_one()
    #     if not self.reservation_event_id:
    #         self.request_reservation()
    #         reserve_event = self.info_calendar_event()
    #         reserve_event.write(
    #             {'state': 'draft'}
    #         )

    # @api.multi
    # def open_resources_reservation(self):
    #     self.ensure_one()
    #     reserve_event = self.info_calendar_event()
    #     reserve_event.write(
    #         {'state': 'open'}
    #     )

    # def info_calendar_event(self):
    #     return self.env['calendar.event']. \
    #         browse(self.reservation_event_id)

    # def do_clone_task_reservation(self):
    #     if self.reservation_event_id:
    #         self.get_calendar_event().write({'state': 'draft'})

    # def do_task_reservation(self):
    #     self.draft_resources_reservation()
    #     if self.task_state not in ['option', 'done']:
    #         self.send_message('option')
    #     self.write({'task_state': 'option'})
    #     self.do_clone_task_reservation()

    # @api.multi
    # def do_reservation(self):
    #     self.ensure_one()
    #     if self.is_activity():
    #         for child in self.child_ids:
    #             child.do_task_reservation()
    #         self.send_message('option')
    #         self.write({'task_state': 'option'})
    #     else:
    #         self.draft_resources_reservation()
    #         self.do_task_reservation()
    #         self.write({'task_state': 'option'})

    # @api.multi
    # def action_cancel(self):
    #     if self.is_type_task() and \
    #             self.task_state in ['requested', 'read', 'postponed',
    #                                 'accepted', 'option']:
    #         self.send_message('canceled')
    #         self.cancel_resources_reservation()
    #         self.reservation_event_id = False
    #         self.write({'task_state': 'canceled'})
    #     elif self.is_activity():
    #         if self.task_state == 'approved':
    #             for child in self.child_ids:
    #                 child.action_cancel()
    #             self.send_message('canceled')
    #             self.write({'task_state': 'canceled'})
    #         elif self.task_state == 'option':
    #             for child in self.child_ids:
    #                 child.action_cancel()
    #             self.write({'task_state': 'canceled'})

    # @api.multi
    # def action_accept(self):
    #     return self.get_confirmation_wizard('accept')

    # @api.multi
    # def action_read(self):
    #     self.open_resources_reservation()
    #     self.write({'task_state': 'read'})

    # @api.multi
    # def action_postpone(self):
    #     if self.is_type_task() and self.task_state in \
    #             ['requested', 'read', 'canceled', 'accepted']:
    #         self.send_message('postponed')
    #     elif self.is_activity():
    #         if self.task_state == 'approved':
    #             for child in self.child_ids:
    #                 child.action_postpone()
    #             self.send_message('postponed')
    #         elif self.task_state == 'option':
    #             for child in self.child_ids:
    #                 child.action_postpone()
    #     self.write({'task_state': 'postponed'})

    # @api.multi
    # def confirm_reservation(self):
    #     self.draft_resources_reservation()
    #     if self.is_type_task() and\
    #             self.check_task_state(self.task_state):
    #         self.send_message('requested')
    #     self.open_resources_reservation()
    #     self.write({'task_state': 'requested'})

    # @api.multi
    # def confirm_accept_reservation(self):
    #     if self.is_activity():
    #         if self.check_task_state(self.task_state):
    #             for child in self.child_ids:
    #                 self.child_reservation(child)
    #         self.write({'task_state': 'approved'})
    #     self.open_resources_reservation()
    #     if self.is_type_task():
    #         self.write({'task_state': 'accepted'})
    #         self.send_message('accepted')

    # def child_reservation(self, child):
    #     child.draft_resources_reservation()
    #     if self.check_task_state(child.task_state):
    #         child.send_message('requested')
    #     child.open_resources_reservation()
    #     child.write({'task_state': 'requested'})

    # @staticmethod
    # def get_message_body_task(action):
    #     switcher = {
    #         'draft': ' ',
    #         'option': _('The following is optional and \
    #                     appears as crosshatched on your calendar'),
    #         'requested': _('The following is requested'),
    #         'accepted': _('The following is approved'),
    #         'read': ' ',
    #         'postponed': _('The following is postponed \
    #                     and no longer appear on your calendars'),
    #         'done': _('The following is done'),
    #         'canceled': _('The following is canceled\
    #                      and no longer on your calendars')
    #     }
    #     return switcher.get(action)

    # def get_message(self, action):
    #     message = '<br>'
    #     if self.is_activity():
    #         message += _('Activity: <br>') + self.name + '<br>'
    #         message += _('Tasks: <br>')
    #         for index_task, task in enumerate(self.child_ids):
    #             message += task.name
    #             if index_task < len(self.child_ids) - 1:
    #                 message += ', '
    #     elif self.activity_task_type == 'task':
    #         message += _('Task: <br>') + self.name
    #     return {
    #         'body': self.get_message_body_task(action) + message,
    #         'channel_ids': [(6, 0, self.message_channel_ids.ids)],
    #         'email_from': 'Administrator <admin@yourcompany.example.com>',
    #         'message_type': 'notification',
    #         'model': 'project.task',
    #         'partner_ids': [(6, 0, self.message_partner_ids.ids)],
    #         'record_name': self.name,
    #         'reply_to': 'Administrator <admin@yourcompany.example.com>',
    #         'res_id': self.id,
    #         'subject': self.code
    #     }

    # def send_message(self, action):
    #     self.env['mail.message'].create(self.get_message(action))

    # def is_resource_booked(self):
    #     if self.room_id:
    #         overlaps = self.env['calendar.event'].search([
    #             ('room_id', '=', self.room_id.id),
    #             ('start', '<', self.date_end),
    #             ('stop', '>', self.date_start),
    #             ('state', '!=', 'cancelled'),
    #         ])
    #         overlaps_ids = overlaps.ids
    #         for calendar_event in overlaps_ids:
    #             if self.env['calendar.event'] \
    #                     .browse(calendar_event).event_task_id.id == self.id:
    #                 overlaps_ids.remove(calendar_event)
    #         if len(overlaps_ids) > 0:
    #             return True
    #     if self.equipment_id:
    #         overlaps_equipment = self.env['calendar.event'].search([
    #             ('equipment_ids', 'in', [self.equipment_id.id]),
    #             ('start', '<', self.date_end),
    #             ('stop', '>', self.date_start),
    #             ('state', '!=', 'cancelled'),
    #         ])
    #         if len(overlaps_equipment) > 0:
    #             return True
    #     return False

    # def is_hr_resource_double_booked(self, attendee,
    #                                  date_start=None, date_end=None):
    #     if not date_start and not date_end:
    #         date_start = self.date_start
    #         date_end = self.date_end
    #     overlaps_partners = self.env['calendar.event'].search([
    #         ('partner_ids', 'in', attendee),
    #         ('start', '<', date_end),
    #         ('stop', '>', date_start),
    #         ('state', '!=', 'cancelled'),
    #     ])

    #     overlaps_partners_ids = overlaps_partners.ids
    #     for overlap_partner_id in overlaps_partners_ids:
    #         if self.env['calendar.event']\
    #                 .browse(overlap_partner_id).event_task_id.id == self.id:
    #             overlaps_partners_ids.remove(overlap_partner_id)

    #     return len(overlaps_partners_ids) > 0

    # @api.multi
    # def get_confirmation_wizard(self, action):
    #     self.ensure_one()
    #     res = self.get_booked_resources()
    #     if res != '':
    #         res = _(MSG_RES) + res
    #     message = _(MSG_CONFIRM) + res + _(MSG_CONTINUE)
    #     new_wizard = self.env['reservation.validation.wiz'].create(
    #         {
    #             'task_id': self.id,
    #             'message': message,
    #             'action': action,
    #         }
    #     )
    #     return {
    #         'name': 'Confirm reservation',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'reservation.validation.wiz',
    #         'target': 'new',
    #         'res_id': new_wizard.id,
    #     }

    # @staticmethod
    # def check_task_state(task_state_in):
    #     return task_state_in in \
    #         ['draft', 'option', 'postponed', 'canceled']

    # @api.multi
    # def _message_track(self, tracked_fields, initial):
    #     mail_track = super()._message_track(tracked_fields, initial)
    #     changes = mail_track[0]
    #     tracking_value_ids = mail_track[1]
    #     if self.activity_task_type == 'activity':
    #         tracking_value_ids = self.order_activity_fields(tracking_value_ids)
    #     elif self.activity_task_type == 'task':
    #         tracking_value_ids = self.order_task_fields(tracking_value_ids)
    #     return changes, tracking_value_ids

    # @staticmethod
    # def order_activity_fields(tracking_values):
    #     activity_fields_list = [
    #         'task_state',
    #         'name',
    #         'code',
    #         'responsible_id',
    #         'partner_id',
    #         'room_id',
    #         'date_start',
    #         'date_end',
    #         'notes',
    #         'project_id',
    #         'category_id',
    #         'resource_type',
    #         'manager_id',
    #         'user_id',
    #         'client_type',
    #         'sector_id'
    #     ]
    #     activity_tracking_values = []
    #     for index in range(len(activity_fields_list)):
    #         for k in range(len(tracking_values)):
    #             activity = tracking_values.__getitem__(k)
    #             if activity.__getitem__(2).get('field')\
    #                     == activity_fields_list[index]:
    #                 activity_tracking_values.append(activity)
    #     return activity_tracking_values

    # @staticmethod
    # def order_task_fields(tracking_values):
    #     task_fields_list = [
    #         'task_state',
    #         'name',
    #         'code',
    #         'responsible_id',
    #         'partner_id',
    #         'date_start',
    #         'date_end',
    #         'notes',
    #         'department_id',
    #         'employee_ids',
    #         'project_id',
    #         'category_id',
    #         'room_id',
    #         'resource_type',
    #         'user_id',
    #         'client_type',
    #         'sector_id',
    #         'rel_date_start',
    #         'rel_date_end',
    #         'report_done_required'
    #     ]
    #     task_tracking_values = []
    #     for x in range(len(task_fields_list)):
    #         for k in range(len(tracking_values)):
    #             task = tracking_values.__getitem__(k)
    #             if task.__getitem__(2).get('field') == task_fields_list[x]:
    #                 task_tracking_values.append(task)
    #     return task_tracking_values
