# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from datetime import datetime


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
    activity_category_id = fields.Many2one(
        'activity.category',
        string='Category',
    )
    task_category_id = fields.Many2one(
        'task.category',
        string='Category',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
    )
    employee_ids = fields.Many2many(
        'hr.employee', 'task_emp_rel',
        'task_id', 'employee_id',
        string='Employees',
    )
    responsible_id = fields.Many2one(
        'res.partner',
        related='project_id.responsible_id',
        readonly=True,
        string='Responsible',
        store=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='project_id.partner_id',
        string='Client',
        store=True,
        readonly=True,
    )
    task_responsible_id = fields.Many2one(
        'res.partner',
        related='parent_id.responsible_id',
        readonly=True,
        string='Responsible',
        store=True,
    )
    task_partner_id = fields.Many2one(
        'res.partner',
        related='parent_id.partner_id',
        string='Client',
        store=True,
        readonly=True,
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
    )
    equipment_id = fields.Many2one(
        string='Equipment',
        comodel_name='resource.calendar.instrument',
        ondelete='set null',
    )
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equip./Service'),
        ('room', 'Room')], string='Resource Type',
        default='room', required=True,
    )
    task_state = fields.Selection([
        ('draft', 'Draft'),
        ('option', 'Option'),
        ('requested', 'Requested'),
        ('read', 'Read'),
        ('accepted', 'Accepted'),
        ('done', 'Done'),
        ('canceled', 'Canceled')],
        string='Task State',
        default='draft',
        track_visibility='onchange',
    )
    notes = fields.Html(string='Notes')
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

    def _compute_project_task_log(self):
        for rec in self:
            rec.project_task_log = self.env['auditlog.log'].search_count([
                ('model_id', '=', self.env.ref(
                    'project.model_project_task').id),
                ('res_id', '=', rec.id)
            ])

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
                    task.task_order = time_difference.days * 24 * 60\
                        + time_difference.seconds / 60

    def action_done(self):
        self.write({'task_state': 'done'})

    @api.multi
    def action_request(self):
        self.draft_resources_reservation()
        self.write({'task_state': 'requested'})

    @api.multi
    def action_option(self):
        if self.activity_task_type == 'task':
            self.draft_resources_reservation()
            if self.task_state in ['requested', 'read', 'accepted']:
                self.send_message("option")
        self.write({'task_state': 'option'})

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
    def action_cancel(self):
        self.write({'task_state': 'canceled'})
        self.cancel_resources_reservation()

    @api.multi
    def action_accept(self):
        self.request_reservation()
        self.write({'task_state': 'accepted'})

    @api.multi
    def action_read(self):
        self.write({'task_state': 'read'})

    @api.multi
    def action_draft(self):
        self.write({'task_state': 'draft'})
        self.draft_resources_reservation()

    def get_message_body(self, action):
        switcher = {
            'draft': ' ',
            'option': _('The following are Optional\
                        and no longer on your calendars'),
            'requested': _('The following is requested'),
            'accepted': ' ',
            'read': ' ',
            'done': ' ',
            'canceled': _('The following is canceled\
                         and no longer on your calendars')
        }
        return switcher.get(action)

    def get_message(self, action):
        return {
            'body': self.get_message_body(action),
            'channel_ids': [(6, 0, [self.env.ref
                            ('project.mail_channel_project_task').id])],
            'email_from': 'Administrator <admin@yourcompany.example.com>',
            'message_type': 'notification',
            'model': 'project.task',
            'partner_ids': [(6, 0, [self.task_responsible_id.id])],
            'record_name': self.name,
            'reply_to': 'Administrator <admin@yourcompany.example.com>',
            'res_id': self.id,
            'subject': self.code
        }

    def send_message(self, action):
        self.env['mail.message'].create(self.get_message(action))
