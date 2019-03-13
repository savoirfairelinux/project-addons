# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Task(models.Model):
    _inherit = ['project.task']
    _rec_name = 'complete_name'

    name = fields.Char(
        string='Title',
        required=True,
        track_visibility='onchange',
    )
    code = fields.Char(
        string='Number',
        track_visibility='onchange',
    )
    complete_name = fields.Char(
        'Complete Name',
        compute='_compute_complete_name',
        store=True
    )
    activity_task_type = fields.Selection(
        [
            ('activity', 'Activity'),
            ('task', 'Task'),
        ],
        string='Type',
    )
    parent_id = fields.Many2one(
        'project.task',
        track_visibility='onchange',
    )
    responsible_id = fields.Many2one(
        'res.partner',
        string='Task/Activity Responsible',
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        track_visibility='onchange',
    )
    client_type = fields.Many2one(
        'res.partner.category.type',
        string='Client Type',
        track_visibility='onchange',
    )
    sector_id = fields.Many2one(
        'res.partner.sector',
        string='Faculty Sectors',
        track_visibility='onchange',
    )
    date_start = fields.Datetime(
        string='Starting Date',
        default=None,
        index=True,
        copy=False,
        track_visibility='onchange',
    )
    date_end = fields.Datetime(
        string='Ending Date',
        index=True,
        copy=False,
        track_visibility='onchange',
    )
    task_order = fields.Integer(
        string='Task order',
        store=True,
        readonly=True,
        compute='_compute_order_task',
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category',
        default=lambda self: self.env['task.category'].search(
            [('is_default', '=', True)]),
        track_visibility='onchange',
    )
    color = fields.Char(related='category_id.color')
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
    user_id = fields.Many2one(
        'res.users',
        string='Created by',
        default=lambda self: self.env.uid,
        index=True,
        track_visibility='onchange',
    )
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equip./Service'),
        ('room', 'Room')],
        string='Resource Type',
        default='room',
        track_visibility='onchange',
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
        track_visibility='onchange',
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
        string='State',
        default='draft',
        track_visibility='onchange',
    )
    task_state_report_done_required = fields.Selection([
        ('draft', 'Draft'),
        ('option', 'Option'),
        ('requested', 'Requested'),
        ('read', 'Read'),
        ('postponed', 'Postponed'),
        ('accepted', 'Accepted'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('canceled', 'Canceled')],
        string='State',
        default='draft',
        compute='_compute_task_state_visible'
    )
    task_state_report_not_done_required = fields.Selection([
        ('draft', 'Draft'),
        ('option', 'Option'),
        ('requested', 'Requested'),
        ('read', 'Read'),
        ('postponed', 'Postponed'),
        ('accepted', 'Accepted'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('canceled', 'Canceled')],
        string='State',
        default='draft',
        compute='_compute_task_state_visible'
    )
    reservation_event_id = fields.Integer(
        string='Reservation event',
    )
    report_done_required = fields.Boolean(
        string='Report done required',
        track_visibility='onchange',
    )
    preceding_task_ids = fields.Many2many(
        string='Preceding tasks',
        comodel_name='project.task',
        relation='project_task_related_rel',
        column1='project_task_id',
        column2='project_task_related_id',
        track_visibility='onchange',
    )
    succeeding_task_ids = fields.Many2many(
        string='Succeeding tasks',
        comodel_name='project.task',
        relation='project_task_related_rel',
        column1='project_task_related_id',
        column2='project_task_id',
        track_visibility='onchange',
    )
    notes = fields.Html(
        string='Notes',
        track_visibility='onchange',
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
    is_from_template = fields.Boolean(
        string='Is Created From Template',
        default=False,
    )
    spectators = fields.Char(
        string='Spectators',
     )

    @api.onchange('spectators')
    def check_numeric(self):
        try:
            int(self.spectators)
        except Exception as exception:
            raise ValidationError(_('The Input value should be numeric'))

    real_date_start = fields.Datetime(
        string='Actual Start Time',
        default=None,
    )
    real_date_end = fields.Datetime(
        string='Actual End Time',
        default=None,
    )
    total_time = fields.Char(
        string='Actual Total Time',
        compute='_compute_actual_total_time',
    )

    @api.one
    @api.depends('real_date_start', 'real_date_end')
    def _compute_actual_total_time(self):
        self.ensure_one()
        if self.real_date_start and self.real_date_end:
            if self.real_date_end > self.real_date_start:
                time_diff = relativedelta(fields.Datetime.from_string(self.real_date_end),
                                          fields.Datetime.from_string(self.real_date_start))
                hours = time_diff.hours
                minutes = time_diff.minutes
                self.total_time = "{0:0=2d}".format(hours) + ":" + "{0:0=2d}".format(minutes)
            elif self.real_date_end == self.real_date_start:
                self.total_time = "0:0"
            else:
                raise ValidationError(_('Actual Start Time should be before Actual End Time'))
        else:
            self.total_time = "00:00"

    @api.depends('name', 'code')
    def _compute_complete_name(self):
        for task in self:
            if task.activity_task_type == 'task':
                task.complete_name = '%s / %s' % (task.code, task.name)
            else:
                task.complete_name = task.name

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
            self.partner_id = self.project_id.partner_id
            self.client_type = self.project_id.client_type

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if self.parent_id:
            if self.parent_id.responsible_id:
                self.responsible_id = self.parent_id.responsible_id
            if self.parent_id.partner_id:
                self.partner_id = self.parent_id.partner_id
                self.client_type = self.parent_id.client_type
            if self.parent_id.category_id:
                self.category_id = self.parent_id.category_id

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

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self._onchange_partner_id()
        if self.parent_id:
            self.client_type = self.parent_id.client_type
            return
        if self.project_id:
            self.client_type = self.project_id.client_type
            return
        if self.partner_id:
            self.client_type = self.partner_id.tag_id.client_type

    def verify_room_bookable(self):
        if self.room_id:
            if not self.room_id.is_bookable:
                raise ValidationError(str(self.room_id.name) + ': ' +
                                      self.get_error_type('ROOM_TYPE_ERROR'))

    def verify_equipment_bookable(self):
        if self.equipment_id:
            if not self.equipment_id.is_bookable:
                raise ValidationError(str(self.equipment_id.name) + ': ' +
                                      self.get_error_type(
                                          'RESOURCE_TYPE_ERROR'))

    def get_error_type(self, type_error):
        error_msg = ""
        if type_error == 'RESOURCE_TYPE_ERROR':
            error_msg = _('this resource is not bookable')
        if type_error == 'ROOM_TYPE_ERROR':
            error_msg = _('this room is not bookable')
        if type_error == 'CLIENT_TYPE_ERROR':
            error_msg = _('There must be a responsible or a client')
        return error_msg

    @api.constrains('parent_id')
    def _check_subtask_project(self):
        for task in self:
            if task.activity_task_type is False:
                super(Task, task)._check_subtask_project()

    @api.model
    def create(self, vals):
        if self.is_new_activity(vals):
            return self.create_activity(vals)
        elif self.is_new_task(vals):
            return self.create_task(vals)
        else:
            return super(Task, self).create(vals)

    def create_main_task(self, vals, parent_id):
        vals['parent_id'] = parent_id
        vals['client_type'] = self.env['project.task']\
            .search([('id', '=', parent_id)]).client_type.id
        vals['message_follower_ids'] = None
        vals['project_id'] = None
        vals['activity_task_type'] = 'task'
        vals['is_main_task'] = True
        self.create_task(vals)

    def is_new_task(self, vals):
        return 'activity_task_type' in vals\
               and vals['activity_task_type'] == 'task'

    def is_new_activity(self, vals):
        return 'activity_task_type' in vals\
               and vals['activity_task_type'] == 'activity'

    def get_is_from_template(self, vals):
        return 'is_from_template' in vals and vals['is_from_template']

    @api.multi
    def create_task(self, vals):
        if self.get_is_from_template(vals):
                vals['message_follower_ids'] = None
        vals['code'] = self.env['ir.sequence'] \
            .next_by_code('project.task.task')
        return super(Task, self).create(vals)

    @api.multi
    def create_activity(self, vals):
        vals['code'] = self.env['ir.sequence'] \
            .next_by_code('project.task.activity')
        children = self.activity_has_children(vals)
        new_activity = super(Task, self).create(vals)
        if not self.get_is_from_template(vals):
            self.create_main_task(vals, new_activity.id)
        if children:
            self.create_children_from_activity_create(children, new_activity.id)
        return new_activity

    def activity_has_children(self, vals):
        if 'child_ids' in vals:
            return vals.pop('child_ids')
        else:
            return False

    def create_children_from_activity_create(self, children, parent_id):
        for child in children:
            child[2]['parent_id'] = parent_id
            self.create_task(child[2])

    @api.multi
    def write(self, vals):
        if self.is_activity():
            return self.write_activity(vals)
        else:
            self.update_reservation_event(vals)
            return super(Task, self).write(vals)

    def is_activity(self):
        return self.activity_task_type == 'activity'

    @api.multi
    def write_activity(self, vals):
        self.write_main_task(vals)
        self.write_children(vals)
        return super(Task, self).write(vals)

    def write_children(self, vals):
        task_vals = {}
        if 'responsible_id' in vals:
            task_vals['responsible_id'] = vals['responsible_id']
        if 'partner_id' in vals:
            task_vals['partner_id'] = vals['partner_id']
        for task in self.child_ids:
            if task == self.get_main_task():
                continue
            if task_vals:
                task.write(task_vals)

    @api.multi
    def write_main_task(self, vals):
        main_task = self.get_main_task()
        temp = []
        if 'task_state' in vals:
            return False
        if 'child_ids' in vals:
            temp = vals.pop('child_ids')
        main_task = main_task.write(vals)
        if temp:
            vals['child_ids'] = temp
        return main_task

    def get_main_task(self):
        return self.env['project.task'].search([
            ('parent_id', '=', self.id),
            ('is_main_task', '=', True)]
        )

    @api.multi
    def update_reservation_event(self, vals):
        if len(self) == 1:
          if self.reservation_event_id:
              reservation_event = self.env['calendar.event'].\
                  browse(self.reservation_event_id)
              field_names = [
                  'date_start', 'date_end', 'equipment_id',
                  'name', 'resource_type', 'room_id', 'client_type',
                  'employee_ids', 'sector_id', 'category_id', 'partner_id',
              ]
              reservation_event.write(
                  self.set_value_reservation_event(field_names, vals)
              )

    def set_value_reservation_event(self, field_names, vals):
        update_vals = {}
        for index in range(0, len(field_names)):
            if field_names[index] in vals:
                if field_names[index] == 'partner_id':
                    update_vals['client_id'] = vals[field_names[index]]
                if field_names[index] == 'date_start':
                    update_vals['start'] = vals[field_names[index]]
                if field_names[index] == 'date_end':
                    update_vals['stop'] = vals[field_names[index]]
                if field_names[index] == 'equipment_id' \
                        and vals['equipment_id']:
                    update_vals.update(self.update_value_equipment_id(vals))
                elif field_names[index] == 'room_id':
                    if vals['room_id']:
                        update_vals.update(self.update_value_room_id(vals))
                    update_vals[field_names[index]] = vals[field_names[index]]
                if field_names[index] == 'employee_ids':
                    partner_ids = []
                    for employee_id in self.employee_ids:
                        if employee_id.user_id:
                            user = self.env['res.users']\
                                .browse(employee_id.user_id.id)
                            partner_ids.append(self.env['res.partner']
                                               .browse(user.partner_id.id))
                    update_vals['partners_ids'] = partner_ids
                    update_vals.update(self.update_value_employee_ids(vals))
                if field_names[index] in ('sector_id',
                                          'category_id',
                                          'resource_type',
                                          'name',
                                          'client_type'):
                    update_vals[field_names[index]] = vals[field_names[index]]
        return update_vals

    def update_value_equipment_id(self, vals):
        set_value = {}
        set_value['equipment_ids'] = \
            [(6, 0, [vals['equipment_id']])]
        set_value['room_id'] = False
        return set_value

    def update_value_room_id(self, vals):
        set_value = {}
        set_value['equipment_ids'] = \
            [(6, 0, self.env['resource.calendar.room'].
              browse(vals['room_id']).instruments_ids.ids)]
        return set_value

    def update_value_employee_ids(self, vals):
        set_value = {}
        set_value['partner_ids'] = [(
            6, 0, self.get_updated_partners(
                vals['employee_ids'][0][2]))]
        return set_value

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name),
                      ('code', operator, name)]
        return super(Task, self).search(domain + args, limit=limit).name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for task in self:
            if task.activity_task_type == 'task':
                name = task.code + '/' + task.name
            else:
                name = task.name
            result.append((task.id, name))
        return result

    @api.depends('task_state')
    def _compute_task_state_visible(self):
        for rec in self:
            rec.task_state_report_done_required = rec.task_state
            rec.task_state_report_not_done_required = rec.task_state

    @api.multi
    @api.depends('date_start', 'parent_id.date_start')
    def _compute_order_task(self):
        for task in self:
            if task.activity_task_type == 'task':
                if task.parent_id and task.parent_id.date_start:
                    activity_date_start = task.parent_id.date_start
                    if task.date_start:
                        task.task_order = self.get_task_order(
                            task.date_start,
                            activity_date_start,
                            '%Y-%m-%d %H:%M:%S'
                        )

    def get_task_order(self, task_ds, activity_ds, format):
        time_diff = datetime.strptime(task_ds, format) \
                    - datetime.strptime(activity_ds, format)
        return time_diff.days * 24 * 60 + time_diff.seconds / 60

    def action_done(self):
        self.open_resources_reservation()
        self.write({'task_state': 'done'})

    @api.multi
    def action_request(self):
        return self.get_confirmation_wizard('request')

    @api.multi
    def action_option(self):
        return self.get_confirmation_wizard('option')

    @api.multi
    def action_return_option(self):
        self.write({'task_state': 'option'})
        if self.is_activity():
            for child in self.child_ids:
                child.write({'task_state': 'option'})
                child.do_clone_task_reservation()
        else:
            self.do_clone_task_reservation()

    def get_booked_resources(self):
        res = ''
        if self.activity_task_type == 'task':
            if self.is_resource_booked():
                res += self.room_id.name + '<br>' if (
                    self.room_id) else self.equipment_id.name + '<br>'
        if self.is_activity():
            for child in self.child_ids:
                if child.is_resource_booked():
                    res += child.room_id.name + \
                           ' - ' + child.date_start + \
                           ' - ' + child.date_end + \
                           ' - ' + child.code + \
                           '<br>' if child.room_id else (
                            child.equipment_id.name + ' - ' +
                            child.date_start + ' - ' + child.date_end +
                            ' - ' + child.code + '<br>'
                            )
        return res

    @api.multi
    def get_partners(self):
        partners = []
        for e in self.employee_ids:
            if e.user_id:
                partners.append(e.user_id.partner_id.id)
        return partners

    @api.multi
    def get_updated_partners(self, employee_ids):
        partner_ids = []
        employee = self.env['hr.employee']
        for e in employee_ids:
            emp = employee.browse(e)
            if emp.user_id:
                partner_ids.append(emp.user_id.partner_id.id)
        return partner_ids

    @api.multi
    def request_reservation(self):
        self.ensure_one()
        calendar_event = self.env['calendar.event']
        values = {
            'start': self.date_start,
            'stop': self.date_end,
            'name': self.complete_name,
            'resource_type': self.resource_type,
            'room_id': self.room_id.id if self.room_id else None,
            'equipment_ids': [(
                4, self.equipment_id.id, 0)] if self.equipment_id else None,
            'partner_ids': [(6, 0, self.get_partners())],
            'client_id': self.partner_id.id,
            'client_type': self.client_type.id,
            'state': 'open',
            'event_task_id': self.id,
            'is_task_event': True,
            'sector_id': self.sector_id.id if self.sector_id else None,
            'category_id': self.category_id.id,
        }
        new_event = calendar_event.create(values)
        self.reservation_event_id = new_event.id
        if self.room_id:
            self.reserve_equipment_inside(new_event.id)

    def get_calendar_event(self):
        self.ensure_one()
        return self.env['calendar.event'].search([('event_task_id', '=', self.id)])

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
        room_id = self.env['resource.calendar.room'].\
            browse(self.room_id).id
        return room_id.instruments_ids.ids

    @api.multi
    def cancel_resources_reservation(self):
        self.ensure_one()
        if self.reservation_event_id:
            reserve_event = self.info_calendar_event()
            reserve_event.write(
                {'state': 'cancelled'}
            )

    @api.multi
    def draft_resources_reservation(self):
        self.ensure_one()
        if not self.reservation_event_id:
            self.request_reservation()
            reserve_event = self.info_calendar_event()
            reserve_event.write(
                {'state': 'draft'}
            )

    @api.multi
    def open_resources_reservation(self):
        self.ensure_one()
        reserve_event = self.info_calendar_event()
        reserve_event.write(
            {'state': 'open'}
        )

    def info_calendar_event(self):
        return self.env['calendar.event'].\
            browse(self.reservation_event_id)

    def do_clone_task_reservation(self):
        if self.reservation_event_id:
            self.get_calendar_event().write({'state': 'draft'})

    def do_task_reservation(self):
        self.draft_resources_reservation()
        if self.task_state not in ['option', 'done']:
            self.send_message('option')
        self.write({'task_state': 'option'})
        self.do_clone_task_reservation()

    @api.multi
    def do_reservation(self):
        self.ensure_one()
        if self.is_activity():
            for child in self.child_ids:
                child.do_task_reservation()
            self.send_message('option')
            self.write({'task_state': 'option'})
        else:
            self.draft_resources_reservation()
            self.do_task_reservation()
            self.write({'task_state': 'option'})

    @api.multi
    def action_cancel(self):
        if self.activity_task_type == 'task' and \
                self.task_state in ['requested', 'read', 'postponed',
                                    'accepted']:
            self.send_message('canceled')
            self.cancel_resources_reservation()
            self.write({'task_state': 'canceled'})
        elif self.is_activity():
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
        return self.get_confirmation_wizard('accept')

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
        elif self.is_activity():
            if self.task_state == 'accepted':
                for child in self.child_ids:
                    child.action_postpone()
                self.send_message('postponed')
            elif self.task_state == 'option':
                for child in self.child_ids:
                    child.action_postpone()
        self.write({'task_state': 'postponed'})

    @api.multi
    def confirm_reservation(self):
        self.draft_resources_reservation()
        if self.activity_task_type == 'task' and self.task_state in [
                'draft', 'option', 'postponed', 'canceled']:
            self.send_message('requested')
        self.open_resources_reservation()
        self.write({'task_state': 'requested'})

    @api.multi
    def confirm_accept_reservation(self):
        if self.is_activity():
            if self.task_state in [
                    'draft', 'option', 'postponed', 'canceled']:
                for child in self.child_ids:
                    self.child_reservation(child)
                self.send_message('requested')
        self.open_resources_reservation()
        self.write({'task_state': 'accepted'})

    def child_reservation(self, child):
        child.draft_resources_reservation()
        if child.task_state in ['draft', 'option', 'postponed',
                                'canceled']:
            child.send_message('requested')
        child.open_resources_reservation()
        child.write({'task_state': 'requested'})

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
        if self.is_activity():
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
                raise ValidationError(self.get_error_type('CLIENT_TYPE_ERROR'))
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

    def is_resource_booked(self):
        if self.room_id:
            overlaps = self.env['calendar.event'].search([
                ('room_id', '=', self.room_id.id),
                ('start', '<', self.date_end),
                ('stop', '>', self.date_start),
            ])
            overlaps_ids = overlaps.ids
            for calendar_event in overlaps_ids:
                if self.env['calendar.event']\
                        .browse(calendar_event).event_task_id.id == self.id:
                    overlaps_ids.remove(calendar_event)
            if len(overlaps_ids) > 0:
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

    @api.multi
    def get_confirmation_wizard(self, action):
        self.ensure_one()
        res = self.get_booked_resources()
        if res != '':
            res = _('The Following resources are already booked:<br>') + res
        message = _('Please Confirm your reservation.<br>') + res + _(
            'Do you want to continue?')
        new_wizard = self.env['reservation.validation.wiz'].create(
            {
                'task_id': self.id,
                'message': message,
                'action': action,
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
