# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class Task(models.Model):
    _inherit = ['project.task']

    name = fields.Char(
        string='Title',
        required=True,
    )
    code = fields.Char(
        string='Number',
    )
    activity_task_type = fields.Selection(
        [
            ('activity', 'Activity'),
            ('task', 'Task'),
        ],
        string='Type',
    )
    date_start = fields.Datetime(
        string='Starting Date',
        default=None,
        index=True,
        copy=False,
        track_visibility='always',
    )
    date_end = fields.Datetime(
        string='Ending Date',
        index=True,
        copy=False,
        track_visibility='always',
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        track_visibility='onchange',
    )
    employee_ids = fields.Many2many(
        'hr.employee', 'task_emp_rel',
        'task_id', 'employee_id',
        string='Employees',
        track_visibility='onchange',
    )
    responsible_id = fields.Many2one(
        'res.partner',
        string='Responsible',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
    )
    task_order = fields.Integer(
        string='Task order',
        store=True,
        readonly=True,
        compute='_compute_order_task',
    )
    room_id = fields.Many2one(
        string='Room',
        comodel_name='resource.calendar.room',
        ondelete='set null',
        track_visibility='onchange',
    )
    equipment_id = fields.Many2one(
        string='Equip./Service',
        comodel_name='resource.calendar.instrument',
        ondelete='set null',
    )
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equip./Service'),
        ('room', 'Room')],
        string='Resource Type',
        default='room',
        required=True,
    )
    task_state = fields.Selection([
        ('draft', 'Draft'),
        ('option', 'Option'),
        ('requested', 'Requested'),
        ('read', 'Read'),
        ('postponed', 'Postponed'),
        ('accepted', 'Accepted'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('canceled', 'Canceled')],
        string='Task State',
        default='draft',
        track_visibility='onchange',
    )
    notes = fields.Html(
        string='Notes',
        track_visibility='onchange',
    )
    is_from_template = fields.Boolean(
        string='Is Created From Template',
        default=False,
    )
    reservation_event_id = fields.Integer(
        string='Reservation event',
    )
    report_done_required = fields.Boolean(
        string='Report done required',
    )
    preceding_task_ids = fields.Many2many(
        string='Preceding tasks',
        comodel_name='project.task',
        relation='project_task_related_rel',
        column1='project_task_id',
        column2='project_task_related_id',
    )
    succeeding_task_ids = fields.Many2many(
        string='Succeeding tasks',
        comodel_name='project.task',
        relation='project_task_related_rel',
        column1='project_task_related_id',
        column2='project_task_id',
    )
    project_task_log = fields.Integer(
        string='Project Task Logs',
        compute='_compute_project_task_log',
    )
    asterisk_validate_record = fields.Char(
        string='*',
        compute='_compute_asterisk_column',
    )
    is_main_task = fields.Boolean(
        string='Is it main Task',
        default=False,
    )
    color = fields.Char(related='category_id.color')

    def _compute_project_task_log(self):
        for rec in self:
            rec.project_task_log = self.env['auditlog.log'].search_count([
                ('model_id', '=', self.env.ref(
                    'project.model_project_task').id),
                ('res_id', '=', rec.id)
            ])

    def _compute_asterisk_column(self):
        for rec in self:
            if rec.report_done_required is True:
                rec.asterisk_validate_record = "*"
            else:
                rec.asterisk_validate_record = " "

    @api.onchange('project_id')
    def onchange_project_id(self):
        self._onchange_project()
        if self.project_id:
            if self.project_id.responsible_id:
                self.responsible_id = self.project_id.responsible_id

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if self.parent_id:
            if self.parent_id.responsible_id:
                self.responsible_id = self.parent_id.responsible_id
            if self.parent_id.partner_id:
                self.partner_id = self.parent_id.partner_id

    @api.onchange('succeeding_task_ids')
    def update_preceding(self):
        self.clean_preceding()
        for succeeding in self.succeeding_task_ids:
            succeeding.preceding_task_ids = [(4, self.id, 0)]

    def clean_preceding(self):
        for succeeding in self.succeeding_task_ids:
            succeeding.preceding_task_ids = [(2, self.id, 0)]

    @api.onchange('preceding_task_ids')
    def update_succeeding(self):
        self.clean_succeeding()
        for preceding in self.preceding_task_ids:
            preceding.succeeding_task_ids = [(4, self.id, 0)]

    def clean_succeeding(self):
        for preceding in self.preceding_task_ids:
            preceding.succeeding_task_ids = [(2, self.id, 0)]

    @api.onchange('resource_type')
    def _onchange_resource_type(self):
        self.room_id = None
        self.equipment_id = None

    @api.onchange('room_id')
    def _onchange_room_id(self):
        self.verify_room_bookable()

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        self.verify_equipment_bookable()

    def verify_room_bookable(self):
        if self.room_id:
            if not self.room_id.is_bookable:
                raise ValidationError(
                        _(
                            'This room is not bookable'
                        )
                    )

    def verify_equipment_bookable(self):
        if self.equipment_id:
            if not self.equipment_id.is_bookable:
                raise ValidationError(
                        _(
                            'This resource is not bookable'
                        )
                    )

    @api.constrains('parent_id')
    def _check_subtask_project(self):
        for task in self:
            if task.activity_task_type is False:
                super(Task, task)._check_subtask_project()

    @api.model
    def create(self, vals):
        if 'activity_task_type' in vals:
            if vals['activity_task_type'] == 'activity':
                return_create = self.create_new_activity(vals)
                if not (
                        'is_from_template' in vals and
                        vals['is_from_template']
                ):
                    vals['parent_id'] = return_create.id
                    vals['message_follower_ids'] = None
                    vals['project_id'] = None
                    vals['activity_task_type'] = 'task'
                    vals['is_main_task'] = True
                    self.create_new_task(vals)
            elif vals['activity_task_type'] == 'task':
                if 'is_from_template' in vals and vals['is_from_template']:
                    vals['message_follower_ids'] = None
                return_create = self.create_new_task(vals)
        else:
            return super(Task, self).create(vals)
        return return_create

    @api.multi
    def create_new_task(self, vals):
        vals['code'] = self.env['ir.sequence'] \
            .next_by_code('project.task.task')
        return super(Task, self).create(vals)

    @api.multi
    def create_new_activity(self, vals):
        vals['code'] = self.env['ir.sequence'] \
            .next_by_code('project.task.activity')
        return super(Task, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.activity_task_type == 'activity':
            self.write_activity(vals)
            self.write_task(vals)
            for task in self.child_ids:
                task.write({'responsible_id': self.responsible_id.id,
                           'partner_id': self.partner_id.id})
        elif self.activity_task_type == 'task':
            return super(Task, self).write(vals)
        else:
            return super(Task, self).write(vals)

    @api.multi
    def write_activity(self, vals):
        return super(Task, self).write(vals)

    @api.multi
    def write_task(self, vals):
        main_task = self.get_main_task()
        if 'child_ids' in vals:
            del vals['child_ids']
        return main_task.write(vals)

    def get_main_task(self):
        return self.env['project.task'].search([
            ('parent_id', '=', self.id),
            ('is_main_task', '=', True)]
        )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name),
                      ('code', operator, name)]
        return super(Task, self).search(domain + args, limit=limit).name_get()

    @api.multi
    @api.depends('date_start', 'parent_id.date_start')
    def _compute_order_task(self):
        for task in self:
            if task.activity_task_type == 'task':
                if task.parent_id and task.parent_id.date_start:
                    activity_date_start = task.parent_id.date_start
                    fmt = '%Y-%m-%d %H:%M:%S'
                    time_difference = \
                        datetime.strptime(task.date_start, fmt)\
                        - datetime.strptime(activity_date_start, fmt)
                    task.task_order = \
                        time_difference.days * 24 * 60 \
                        + time_difference.seconds / 60

    def action_done(self):
        self.open_resources_reservation()
        self.write({'task_state': 'done'})

    @api.multi
    def action_request(self):
        self.draft_resources_reservation()
        if self.activity_task_type == 'task' and \
                self.task_state in ['draft', 'option', 'postponed', 'canceled']:
            self.send_message('requested')
        self.open_resources_reservation()
        self.write({'task_state': 'requested'})

    @api.multi
    def action_option(self):
        self.ensure_one()
        res = ''
        if self.activity_task_type == 'task':
            if self.check_resource_booked():
                res += self.room_id.name + '<br>' if (
                    self.room_id) else self.equipment_id.name + '<br>'
        if self.activity_task_type == 'activity':
            for child in self.child_ids:
                if child.check_resource_booked():
                    res += child.room_id.name + '<br>' if (
                        child.room_id) else child.equipment_id.name + '<br>'
        if res != '':
            res = _('The Following resources are already booked:<br>') + res
        message = _('Please Confirm your reservation.<br>') + res + _(
            'Do you want to continue?')
        new_wizard = self.env['reservation.validation.wiz'].create(
            {
                'task_id': self.id,
                'message': message
            }
        )

        return {
            'name': 'Confirm reservation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reservation.validation.wiz',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    @api.multi
    def request_reservation(self):
        self.ensure_one()
        calendar_event = self.env['calendar.event']
        values = {
            'start': self.date_start,
            'stop': self.date_end,
            'name': self.name,
            'resource_type': self.resource_type,
            'room_id': self.room_id.id if self.room_id else None,
            'equipment_ids': [(4, self.equipment_id.id, 0)] if self.equipment_id else None,
            'state': 'open'
        }
        new_event = calendar_event.create(values)
        self.reservation_event_id = new_event.id
        if self.room_id:
            self.reserve_equipment_inside(new_event.id)

    @api.multi
    def reserve_equipment_inside(self, event_id):
        self.ensure_one()
        calendar_event = self.env['calendar.event'].browse(event_id)
        calendar_event.write(
            {
                'equipment_ids': [(6, 0, self.get_equipment_ids_inside())]
            })

    @api.multi
    def get_equipment_ids_inside(self):
        room_id = self.env['resource.calendar.room'].browse(self.room_id).id
        return room_id.instruments_ids.ids

    @api.multi
    def cancel_resources_reservation(self):
        self.ensure_one()
        if self.reservation_event_id:
            reservation_event = self.env['calendar.event'].browse(
                self.reservation_event_id)
        reservation_event.write(
            {
                'state': 'cancelled'
            }
        )

    @api.multi
    def draft_resources_reservation(self):
        self.ensure_one()
        if not self.reservation_event_id:
            self.request_reservation()
        reservation_event = self.env['calendar.event'].browse(
            self.reservation_event_id)
        reservation_event.write(
            {
                'state': 'draft'
            }
        )

    @api.multi
    def open_resources_reservation(self):
        self.ensure_one()
        reservation_event = self.env['calendar.event'].browse(
            self.reservation_event_id)
        reservation_event.write(
            {
                'state': 'open'
            }
        )

    @api.multi
    def action_cancel(self):
        if self.activity_task_type == 'task' and \
                self.task_state in ['requested', 'read', 'postponed', 'accepted']:
            self.send_message('canceled')
            self.cancel_resources_reservation()
            self.write({'task_state': 'canceled'})
        elif self.activity_task_type == 'activity':
            if self.task_state == 'accepted':
                for child in self.child_ids:
                    child.action_cancel()
                self.send_message('canceled')
                self.write({'task_state': 'canceled'})
            elif self.task_state == 'option':
                for child in self.child_ids:
                    child.action_cancel()
                self.write({'task_state': 'canceled'})

    @api.multi
    def action_accept(self):
        if self.activity_task_type == 'activity':
            if self.task_state in ['draft', 'option', 'postponed', 'canceled']:
                for child in self.child_ids:
                    child.action_request()
                self.send_message('requested')
        self.open_resources_reservation()
        self.write({'task_state': 'accepted'})

    @api.multi
    def action_read(self):
        self.open_resources_reservation()
        self.write({'task_state': 'read'})

    @api.multi
    def action_draft(self):
        self.write({'task_state': 'draft'})
        self.draft_resources_reservation()

    @api.multi
    def action_postpone(self):
        if self.activity_task_type == 'task' and \
                self.task_state in ['requested', 'read', 'canceled', 'accepted']:
            self.draft_resources_reservation()
            self.send_message('postponed')
        elif self.activity_task_type == 'activity':
            if self.task_state == 'accepted':
                for child in self.child_ids:
                    child.action_postpone()
                self.send_message('postponed')
            elif self.task_state == 'option':
                for child in self.child_ids:
                    child.action_postpone()
        self.write({'task_state': 'postponed'})

    def get_message_body(self, action):
        switcher = {
            'draft': ' ',
            'option': _('The following is Optional and \
                        appears as crosshatched on your calendar'),
            'requested': _('The following is requested'),
            'accepted': _('The following is approved'),
            'read': ' ',
            'postponed': _('The following is postponed \
                        and no longer appear on your calendars'),
            'done': ' ',
            'canceled': _('The following is canceled\
                         and no longer on your calendars')
        }
        return switcher.get(action)

    def get_message(self, action):
        message = '<br>'
        if self.activity_task_type == 'activity':
            responsible = self.responsible_id.id
            message += _('Activity: <br>') + self.name + '<br>'
            message += _('Tasks: <br>')
            for index_task, task in enumerate(self.child_ids):
                message += task.name
                if index_task < len(self.child_ids) - 1:
                    message += ', '
        elif self.activity_task_type == 'task':
            responsible = self.responsible_id.id
            message += _('Task: <br>') + self.name
        # At this moment, there is no requirement to whom the message
        # will be sent
        if not responsible:
            if self.partner_id:
                responsible = self.partner_id
            else:
                raise ValidationError(
                    _(
                        'There must be a responsible or a client ',
                    )
                )
        return {
            'body': self.get_message_body(action) + message,
            'channel_ids': [(6, 0, [self.env.ref
                                    ('project.mail_channel_project_task_event').id])],
            'email_from': 'Administrator <admin@yourcompany.example.com>',
            'message_type': 'notification',
            'model': 'project.task',
            'partner_ids': [(6, 0, [responsible])],
            'record_name': self.name,
            'reply_to': 'Administrator <admin@yourcompany.example.com>',
            'res_id': self.id,
            'subject': self.code
        }

    def send_message(self, action):
        self.env['mail.message'].create(self.get_message(action))

    def check_resource_booked(self):
        if self.room_id:
            overlaps = self.env['calendar.event'].search([
                ('room_id', '=', self.room_id.id),
                ('start', '<', self.date_end),
                ('stop', '>', self.date_start),
            ])
            if len(overlaps) > 0:
                return True
        if self.equipment_id:
            overlaps_equipment = self.env['calendar.event'].search([
                ('equipment_ids', 'in', [self.equipment_id.id]),
                ('start', '<', self.date_end),
                ('stop', '>', self.date_start),
            ])
            if len(overlaps_equipment) > 0:
                return True
        return False

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)") % self.name
        if 'remaining_hours' not in default:
            default['remaining_hours'] = self.planned_hours
        default['task_state'] = 'draft'
        return super(Task, self).copy(default)
