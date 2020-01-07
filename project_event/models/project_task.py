# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import babel.dates
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, AccessError

MINUTES_IN_HOUR = 60
CONVERT_SECONDS_TO_MINUTE = 60
HOURS_IN_DAY = 24
MIN_SPECTATORS_VALUES_LIMIT = 0
MAX_SPECTATORS_VALUES_LIMIT = 1000000

MSG_RES = 'The following resources are already booked:<br>'
MSG_CONFIRM = 'Please confirm your reservation.<br>'
MSG_CONTINUE = 'Do you want to continue?'


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
    task_order = fields.Integer(
        string='Task order',
        store=True,
        readonly=True,
        compute='_compute_order_task',
    )
    reservation_event_id = fields.Integer(
        string='Reservation event',
    )
    report_done_required = fields.Boolean(
        string='Report done required',
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
        string='Is Main Task',
        default=False,
    )
    is_from_template = fields.Boolean(
        string='Is Created From Template',
        default=False,
    )
    spectators = fields.Char(
        string='Spectators',
        size=10,
        default='-',
    )
    table_child_ids = fields.Char(
        store=False
    )
    actual_total_time = fields.Char(
        string='Actual Total Time',
        compute='_compute_actual_total_time',
    )
    color = fields.Char(
        related='category_id.color'
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
    real_date_start = fields.Datetime(
        string='Actual Start Time',
    )
    real_date_end = fields.Datetime(
        string='Actual End Time',
    )
    font_color = fields.Selection([
        ('black', 'Black (Default)'),
        ('white', 'White')],
        related='category_id.font_color'
    )
    activity_task_type = fields.Selection(
        [
            ('activity', 'Activity'),
            ('task', 'Task'),
        ],
        string='Type',
    )
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equipment'),
        ('room', 'Room')],
        string='Resource Type',
        default='room',
        track_visibility='onchange',
    )
    task_state = fields.Selection([
        ('draft', 'Draft'),
        ('option', 'Option'),
        ('requested', 'Requested'),
        ('read', 'Read'),
        ('accepted', 'Accepted'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('postponed', 'Postponed'),
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
        string='Faculty Sector',
        track_visibility='onchange',
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category',
        default=lambda self: self.env['task.category'].search(
            [('is_default', '=', True)]),
        track_visibility='onchange',
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
    user_id = fields.Many2one(
        'res.users',
        string='Created by',
        default=lambda self: self.env.uid,
        index=True,
        track_visibility='onchange',
    )
    room_id = fields.Many2one(
        string='Room',
        comodel_name='resource.calendar.room',
        ondelete='set null',
        track_visibility='onchange',
    )
    equipment_id = fields.Many2one(
        string='Equipment',
        comodel_name='resource.calendar.instrument',
        ondelete='set null',
        track_visibility='onchange',
    )
    service_id = fields.Many2one(
        string='Service',
        comodel_name='resource.calendar.service',
        ondelete='set null',
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

    parent_id_project_id = fields.Many2one(
        related='parent_id.project_id',
        string="Event"
    )
    plan_ids = fields.Many2many(
        comodel_name='project.event.plan',
        string="Plans"
    )

    def format_date(self, date_to_format, format_str='dd-MMMM-yyyy HH:mm:ss'):
        lang = self.env['res.users'].browse(self.env.uid).lang or 'en_US'
        tz = self.env['res.users'].browse(self.env.uid).tz or 'utc'
        if not isinstance(date_to_format, datetime):
            date_to_format = datetime.strptime(
                date_to_format, '%Y-%m-%d %H:%M:%S'
            )
        return babel.dates.format_datetime(
            date_to_format,
            tzinfo=tz,
            format=format_str,
            locale=lang)

    @api.constrains('date_start', 'date_end')
    def _check_closing_date(self):
        if self.date_start and self.date_end and self.date_end < self.\
                date_start:
            raise ValidationError(
                _('Ending date cannot be set before starting date.') + "\n" +
                _("%s '%s' starts '%s' and ends '%s'") %
                (_('Activity') if self.is_activity() else _('Task'), self.name,
                 self.format_date(self.date_start),
                 self.format_date(self.date_end))
            )

    @api.multi
    def subscribe_employees_to_task(self):
        if self.get_partners():
            self.message_subscribe(list(self.get_partners()), force=False)

    @api.model
    def create(self, vals):
        if self.is_new_activity(vals):
            return self.create_activity(vals)
        elif self.is_new_task(vals):
            return self.create_task(vals)
        else:
            return super(Task, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.is_activity():
            return self.write_activity(vals)
        else:
            self.verify_field_access_task_write(vals)
            self.update_reservation_event(vals)
            if 'employee_ids' in vals:
                self.message_unsubscribe(list(
                    self.get_partners()))
                if vals['employee_ids'][0][2]:
                    self.message_subscribe(list(self.get_partners(
                        vals['employee_ids'][0][2])), force=False)
                else:
                    self.message_subscribe(list([]), force=False)

            return super(Task, self).write(vals)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)") % self.name
        if 'remaining_hours' not in default:
            default['remaining_hours'] = self.planned_hours
        default['task_state'] = 'draft'
        default['reservation_event_id'] = False
        new_copy = super(Task, self).copy(default)
        if self.is_activity():
            child_default_vals = {'parent_id': new_copy.id}
            for child in self.child_ids:
                if 'name' in child_default_vals:
                    child_default_vals.pop('name')
                if child.is_main_task:
                    continue
                child.copy(default=child_default_vals)
        return new_copy

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name),
                      ('code', operator, name)]
        return super(Task, self).search(domain + args, limit=limit).name_get()

    @api.one
    @api.depends('real_date_start', 'real_date_end')
    def _compute_actual_total_time(self):
        self.ensure_one()
        if self.real_date_start and self.real_date_end:
            if self.real_date_end > self.real_date_start:
                time_diff = relativedelta(
                    fields.Datetime.from_string(
                        self.real_date_end), fields.Datetime.from_string(
                        self.real_date_start))
                hours = time_diff.hours
                minutes = time_diff.minutes
                self.actual_total_time = "{0:0=2d}".format(
                    hours) + ":" + "{0:0=2d}".format(minutes)
            elif self.real_date_end == self.real_date_start:
                self.actual_total_time = "00:00"
            else:
                raise ValidationError(
                    _('Actual Start Time should be before Actual End Time'))
        else:
            self.actual_total_time = "00:00"

    @api.depends('name', 'code')
    def _compute_complete_name(self):
        for task in self:
            if task.is_type_task():
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

    @api.onchange('spectators')
    def onchange_spectators(self):
        if self.spectators:
            if self.spectators == '-':
                return
            try:
                valid_spectators = int(self.spectators)
            except Exception:
                raise ValidationError(_('Spectators value should be numeric'))
            if valid_spectators >= MIN_SPECTATORS_VALUES_LIMIT and \
                    valid_spectators < MAX_SPECTATORS_VALUES_LIMIT:
                self.spectators = valid_spectators
            else:
                raise ValidationError(
                    _('Spectators value should be in the range[') +
                    str(MIN_SPECTATORS_VALUES_LIMIT) +
                    '-' + str(MAX_SPECTATORS_VALUES_LIMIT) + ']')
        else:
            self.spectators = '0'

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

    @api.onchange('preceding_task_ids')
    def update_succeeding(self):
        self.clean_succeeding()
        for preceding in self.preceding_task_ids:
            preceding.succeeding_task_ids = [(4, self.id, 0)]

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
        if self.partner_id:
            self.client_type = self.partner_id.tag_id.client_type

    @api.constrains('parent_id')
    def _check_subtask_project(self):
        for task in self:
            if task.activity_task_type is False:
                super(Task, task)._check_subtask_project()

    def clean_preceding(self):
        for succeeding in self.succeeding_task_ids:
            succeeding.preceding_task_ids = [(2, self.id, 0)]

    def clean_succeeding(self):
        for preceding in self.preceding_task_ids:
            preceding.succeeding_task_ids = [(2, self.id, 0)]

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

    @staticmethod
    def get_error_type(type_error):
        error_msg = ""
        if type_error == 'RESOURCE_TYPE_ERROR':
            error_msg = _('this resource is not bookable')
        if type_error == 'ROOM_TYPE_ERROR':
            error_msg = _('this room is not bookable')
        if type_error == 'CLIENT_TYPE_ERROR':
            error_msg = _('There must be a responsible or a client')
        return error_msg

    def create_main_task(self, vals, parent_id):
        vals['parent_id'] = parent_id
        vals['client_type'] = self.env['project.task'] \
            .search([('id', '=', parent_id)]).client_type.id
        vals['message_follower_ids'] = None
        vals['project_id'] = None
        vals['activity_task_type'] = 'task'
        vals['is_main_task'] = True
        self.create_task(vals)

    @staticmethod
    def is_new_task(vals):
        return 'activity_task_type' in vals\
               and vals['activity_task_type'] == 'task'

    @staticmethod
    def is_new_activity(vals):
        return 'activity_task_type' in vals\
               and vals['activity_task_type'] == 'activity'

    @staticmethod
    def get_is_from_template(vals):
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
            self.create_children_from_activity_create(
                children, new_activity.id)
        return new_activity

    @staticmethod
    def activity_has_children(vals):
        if 'child_ids' in vals:
            return vals.pop('child_ids')
        else:
            return False

    def create_children_from_activity_create(self, children, parent_id):
        for child in children:
            child[2]['parent_id'] = parent_id
            self.create_task(child[2])

    def is_activity(self):
        return self.activity_task_type == 'activity'

    def is_type_task(self):
        return self.activity_task_type == 'task'

    @api.multi
    def write_activity(self, vals):
        self.verify_field_access_activity_write(vals)
        self.write_children(vals)
        updated_task = super(Task, self).write(vals)
        self.write_main_task(vals)
        return updated_task

    def write_children(self, vals):
        task_vals = {}
        if 'responsible_id' in vals:
            task_vals['responsible_id'] = vals['responsible_id']
        if 'partner_id' in vals:
            task_vals['partner_id'] = vals['partner_id']
        if 'client_type' in vals:
            task_vals['client_type'] = vals['client_type']
        if 'sector_id' in vals:
            task_vals['sector_id'] = vals['sector_id']
        for task in self.child_ids:
            if task == self.get_main_task():
                continue
            if task_vals:
                task.write(task_vals)

    def verify_field_access_task_write(self, vals):
        if self.task_state in ['requested', 'accepted'] and\
                ('description' in vals or 'plan_ids' in vals):
            if self.user_has_groups(
                    'project_event.group_project_event_editor'):
                return
            else:
                raise AccessError(
                    _('You cannot edit fields description and plans'))
        elif self.task_state in ['done'] and 'description' in vals:
            raise AccessError(
                _('You cannot edit fields description and plans in state "done"'))

    def verify_field_access_activity_write(self, vals):
        if self.task_state == 'approved' and self.user_has_groups(
                'project_event.group_project_event_user') and not \
                self.user_has_groups(
                'project_event.group_project_event_editor'):
            allowed_keys = ('spectators', 'notes')
            if not set(vals).issubset(allowed_keys):
                raise AccessError(
                    _('You can only edit field notes and spectators'))

    @api.multi
    def write_main_task(self, vals):
        main_task = self.get_main_task()
        vals.pop('project_id', None)
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

    def get_parent_project_id(self):
        if self.parent_id and self.parent_id.project_id:
            return self.parent_id.project_id.id
        return False

    @api.multi
    def update_reservation_event(self, vals):
        if len(self) == 1:
            if self.reservation_event_id:
                reservation_event = self.env['calendar.event']. \
                    browse(self.reservation_event_id)
                field_names = [
                    'date_start', 'date_end', 'equipment_id',
                    'name', 'resource_type', 'room_id', 'client_type',
                    'employee_ids', 'sector_id', 'category_id', 'partner_id',
                ]
                reservation_event.sudo().write(
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
                    update_vals['partners_ids'] = self\
                        .get_partners()
                    update_vals.update(self.update_value_employee_ids(vals))
                if field_names[index] in ('sector_id',
                                          'category_id',
                                          'resource_type',
                                          'name',
                                          'client_type'):
                    update_vals[field_names[index]] = vals[field_names[index]]
        return update_vals

    @staticmethod
    def update_value_equipment_id(vals):
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

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for task in self:
            if task.is_type_task():
                name = task.code + '/' + task.name
            else:
                name = task.name
            result.append((task.id, name))
        return result

    @staticmethod
    def get_task_order(task_ds, activity_ds, format):
        time_diff = datetime.strptime(task_ds, format) \
            - datetime.strptime(activity_ds, format)
        return time_diff.days * HOURS_IN_DAY * MINUTES_IN_HOUR \
            + time_diff.seconds / CONVERT_SECONDS_TO_MINUTE

    def action_done(self):
        self.open_resources_reservation()
        self.write({'task_state': 'done'})
        self.send_message('done')

    @api.multi
    def action_request(self):
        return self.get_confirmation_wizard('request')

    @api.multi
    def action_option(self):
        return self.get_confirmation_wizard('option')

    @api.multi
    def action_return_option(self):
        return self.get_confirmation_wizard('option')

    def get_booked_resources(self):
        res = ''
        if self.is_type_task() and self.is_resource_booked():
            if self.room_id:
                res += self.room_id.name + '<br>'
                room_instruments = self.env['resource.calendar.room']\
                    .browse(self.room_id.id).instruments_ids
                if len(room_instruments) > 0:
                    for instrument in room_instruments:
                        res += instrument.name + '<br>'
            else:
                res += self.equipment_id.name + '<br>'
        for attendee in self.get_partners():
            hres = self.is_hr_resource_double_booked(attendee)
            partner_attendee = self.env['res.partner'].browse(attendee)
            if hres and partner_attendee:
                res += partner_attendee.name + '<br>'
        if self.is_activity():
            for child in self.child_ids:
                if child.is_resource_booked():
                    res += child.room_id.name + \
                        ' - ' + self.format_date(child.date_start) + \
                        ' - ' + self.format_date(child.date_end) + \
                        ' - ' + child.code + \
                        '<br>' if child.room_id else (
                            child.equipment_id.name + ' - ' +
                            self.format_date(child.date_start) +
                            ' - ' +
                            self.format_date(child.date_end) +
                            ' - ' + child.code + '<br>')
                for attendee in child.get_partners():
                    hres = child.is_hr_resource_double_booked(attendee)
                    attendee_partner = self.env['res.partner'].browse(attendee)
                    if hres and attendee_partner:
                        res += attendee_partner.name +\
                            ' - ' + self.format_date(child.date_start) +\
                            ' - ' + self.format_date(child.date_end) +\
                            ' - ' + child.code +\
                            '<br>'
        return res

    def get_double_booked_resources(self, room_id=None,
                                    equipment_id=None,
                                    employee_ids=None,
                                    date_start=None, date_end=None):

        booked_resources = []
        if not date_end and not date_start:
            date_start = self.date_start
            date_end = self.date_end

        if not room_id:
            room_id = self.room_id.id

        if not equipment_id:
            equipment_id = self.equipment_id.id

        if not employee_ids:
            partner_ids = self.get_partners()
        else:
            partner_ids = self.get_partners(employee_ids)

        if self.room_id:
            overlaps = self.env['calendar.event'].search([
                ('room_id', '=', room_id),
                ('start', '<', date_end),
                ('stop', '>', date_start),
                ('state', '!=', 'cancelled'),
            ])
            overlaps_ids = overlaps.ids
            for overlap_id in overlaps_ids:
                if self.env['calendar.event']\
                        .browse(overlap_id).event_task_id.id == self.id:
                    overlaps_ids.remove(overlap_id)
            if len(overlaps_ids) > 0:
                booked_resources.append(self.env['resource.calendar.room']
                                        .browse(room_id).name)

        overlaps_equipment = self.env['calendar.event'].search([
            ('equipment_ids', 'in', [equipment_id]),
            ('start', '<', date_end),
            ('stop', '>', date_start),
            ('state', '!=', 'cancelled'),
        ])
        overlaps_equipment_ids = overlaps_equipment.ids
        for overlap_equipment_id in overlaps_equipment_ids:
            if self.env['calendar.event']\
                    .browse(overlap_equipment_id)\
                    .event_task_id.id == self.id:
                overlaps_equipment_ids.remove(overlap_equipment_id)
        if len(overlaps_equipment_ids) > 0:
            booked_resources.append(self.env['resource.calendar.instrument']
                                        .browse(equipment_id).name)

        for attendee in partner_ids:
            h_res = self.is_hr_resource_double_booked(attendee)
            partner_attendee = self.env['res.partner'].browse(attendee)
            if h_res and partner_attendee:
                booked_resources.append(partner_attendee.name)

        return booked_resources

    @api.multi
    def get_partners(self, employee_ids=None):
        if not employee_ids:
            employees = self.employee_ids
        else:
            employees = self.env['hr.employee']\
                .search([('id', 'in', employee_ids)])
        partners = []
        for e in employees:
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
        return self.env['calendar.event'].search(
            [('event_task_id', '=', self.id)])

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
        room_id = self.env['resource.calendar.room']. \
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
            reserve_event.event_task_id = False

    @api.multi
    def draft_resources_reservation(self):
        self.ensure_one()
        self.subscribe_employees_to_task()
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
        return self.env['calendar.event']. \
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
            self.do_task_reservation()
            self.write({'task_state': 'option'})

    @api.multi
    def action_cancel(self):
        if self.is_type_task() and \
                self.task_state in ['requested', 'read', 'postponed',
                                    'accepted', 'option']:
            self.send_message('canceled')
            self.cancel_resources_reservation()
            self.reservation_event_id = False
            self.write({'task_state': 'canceled'})
        elif self.is_activity():
            if self.task_state == 'approved':
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
    def action_postpone(self):
        if self.is_type_task() and self.task_state in \
                ['requested', 'read', 'canceled', 'accepted', 'option']:
            self.send_message('postponed')
        elif self.is_activity():
            if self.task_state == 'approved':
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
        if self.is_type_task() and\
                self.check_task_state(self.task_state):
            self.send_message('requested')
        self.open_resources_reservation()
        self.write({'task_state': 'requested'})

    @api.multi
    def confirm_accept_reservation(self):
        if self.is_activity():
            if self.check_task_state(self.task_state):
                for child in self.child_ids:
                    self.child_reservation(child)
            self.write({'task_state': 'approved'})
        self.open_resources_reservation()
        if self.is_type_task():
            self.write({'task_state': 'accepted'})
            self.send_message('accepted')

    def child_reservation(self, child):
        child.draft_resources_reservation()
        if self.check_task_state(child.task_state):
            child.send_message('requested')
        child.open_resources_reservation()
        child.write({'task_state': 'requested'})

    @staticmethod
    def get_message_body_task(action):
        switcher = {
            'draft': ' ',
            'option': _('The following is optional and \
                        appears as crosshatched on your calendar'),
            'requested': _('The following is requested'),
            'accepted': _('The following is approved'),
            'read': ' ',
            'postponed': _('The following is postponed \
                        and no longer appear on your calendars'),
            'done': _('The following is done'),
            'canceled': _('The following is canceled\
                         and no longer on your calendars')
        }
        return switcher.get(action)

    def get_message(self, action):
        message = '<br>'
        if self.is_activity():
            message += _('Activity: <br>') + self.name + '<br>'
            message += _('Tasks: <br>')
            for index_task, task in enumerate(self.child_ids):
                message += task.name
                if index_task < len(self.child_ids) - 1:
                    message += ', '
        elif self.activity_task_type == 'task':
            message += _('Task: <br>') + self.name
        return {
            'body': self.get_message_body_task(action) + message,
            'channel_ids': [(6, 0, self.message_channel_ids.ids)],
            'email_from': 'Administrator <admin@yourcompany.example.com>',
            'message_type': 'notification',
            'model': 'project.task',
            'partner_ids': [(6, 0, self.message_partner_ids.ids)],
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
                ('state', '!=', 'cancelled'),
            ])
            overlaps_ids = overlaps.ids
            for calendar_event in overlaps_ids:
                if self.env['calendar.event'] \
                        .browse(calendar_event).event_task_id.id == self.id:
                    overlaps_ids.remove(calendar_event)
            if len(overlaps_ids) > 0:
                return True
        if self.equipment_id:
            overlaps_equipment = self.env['calendar.event'].search([
                ('equipment_ids', 'in', [self.equipment_id.id]),
                ('start', '<', self.date_end),
                ('stop', '>', self.date_start),
                ('state', '!=', 'cancelled'),
            ])
            if len(overlaps_equipment) > 0:
                return True
        return False

    def is_hr_resource_double_booked(self, attendee,
                                     date_start=None, date_end=None):
        if not date_start and not date_end:
            date_start = self.date_start
            date_end = self.date_end
        overlaps_partners = self.env['calendar.event'].search([
            ('partner_ids', 'in', attendee),
            ('start', '<', date_end),
            ('stop', '>', date_start),
            ('state', '!=', 'cancelled'),
        ])

        overlaps_partners_ids = overlaps_partners.ids
        for overlap_partner_id in overlaps_partners_ids:
            if self.env['calendar.event']\
                    .browse(overlap_partner_id).event_task_id.id == self.id:
                overlaps_partners_ids.remove(overlap_partner_id)

        return len(overlaps_partners_ids) > 0

    @api.multi
    def get_confirmation_wizard(self, action):
        self.ensure_one()
        res = self.get_booked_resources()
        if res != '':
            res = _(MSG_RES) + res
        message = _(MSG_CONFIRM) + res + _(MSG_CONTINUE)
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

    @staticmethod
    def check_task_state(task_state_in):
        return task_state_in in \
            ['draft', 'option', 'postponed', 'canceled']

    @api.multi
    def _message_track(self, tracked_fields, initial):
        mail_track = super()._message_track(tracked_fields, initial)
        changes = mail_track[0]
        tracking_value_ids = mail_track[1]
        if self.activity_task_type == 'activity':
            tracking_value_ids = self.order_activity_fields(tracking_value_ids)
        elif self.activity_task_type == 'task':
            tracking_value_ids = self.order_task_fields(tracking_value_ids)
        return changes, tracking_value_ids

    @staticmethod
    def order_activity_fields(tracking_values):
        activity_fields_list = [
            'task_state',
            'name',
            'code',
            'responsible_id',
            'partner_id',
            'room_id',
            'date_start',
            'date_end',
            'notes',
            'project_id',
            'category_id',
            'resource_type',
            'manager_id',
            'user_id',
            'client_type',
            'sector_id'
        ]
        activity_tracking_values = []
        for index in range(len(activity_fields_list)):
            for k in range(len(tracking_values)):
                activity = tracking_values.__getitem__(k)
                if activity.__getitem__(2).get('field')\
                        == activity_fields_list[index]:
                    activity_tracking_values.append(activity)
        return activity_tracking_values

    @staticmethod
    def order_task_fields(tracking_values):
        task_fields_list = [
            'task_state',
            'name',
            'code',
            'responsible_id',
            'partner_id',
            'date_start',
            'date_end',
            'notes',
            'department_id',
            'employee_ids',
            'project_id',
            'category_id',
            'room_id',
            'resource_type',
            'user_id',
            'client_type',
            'sector_id',
            'rel_date_start',
            'rel_date_end',
            'report_done_required'
        ]
        task_tracking_values = []
        for x in range(len(task_fields_list)):
            for k in range(len(tracking_values)):
                task = tracking_values.__getitem__(k)
                if task.__getitem__(2).get('field') == task_fields_list[x]:
                    task_tracking_values.append(task)
        return task_tracking_values
