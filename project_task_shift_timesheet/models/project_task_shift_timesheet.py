# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
import datetime


class TaskShiftTimesheet(models.Model):
    _name = 'shift.timesheet'

    name = fields.Char(
        compute='_compute_default_name'
    )
    active = fields.Boolean(
        default=True
    )
    activity_id = fields.Many2one(
        'project.task',
        track_visibility='onchange',
        domain="[('activity_task_type', 'in', ['activity'])]",
    )
    activity_code = fields.Char(
        string='Number'
    )
    activity_date = fields.Datetime(
        compute='_compute_activity_date',
        store=True
    )
    department = fields.Many2one(
        'hr.department',
        track_visibility='onchange',
    )
    function = fields.Many2one(
        'resource.calendar.service',
        track_visibility='onchange',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        track_visibility='onchange',
        default=lambda self: self.env['hr.employee'].search([
            ('user_id', '=', self.env.user.id)])[0]
        if self.env['hr.employee'].search([
            ('user_id', '=', self.env.user.id)]) else None
    )
    shift = fields.Integer(default=1)
    start_hour = fields.Integer(
        string='Starting hour',
    )
    start_minute = fields.Integer(
        string='Starting minute',
    )
    end_hour = fields.Integer(
        string='Ending hour',
    )
    end_minute = fields.Integer(
        string='Ending minute',
    )
    duration = fields.Float(
        string='Duration',
        compute='_compute_duration',
    )
    shift_status = fields.Boolean(
        default=False
    )
    compute_dep = fields.Char(
        default=lambda self: self._compute_dep(),
        store=False)
    compute_function = fields.Char(
        default=lambda self: self._compute_function(),
        sore=False)
    _sql_constraints = [
        ('check_shift_start_and_end_time',
         "CHECK ((start_hour < end_hour)) ",
         _('Start time must be before end time')),
        ('check_hours',
         "CHECK ("
         "(start_hour >= 0) AND ( start_hour < 24) AND"
         "(end_hour >= 0) AND ( end_hour < 24)) ",
         _('Please enter hours between 0 and 24 hours')),
        ('check_minutes',
         "CHECK ("
         "(start_minute >= 0) AND ( start_minute < 60) AND"
         "(end_minute >= 0) AND ( end_minute < 60)) ",
         _('Please enter minutes between 0 and 59 minutes')),
    ]

    @api.one
    def _compute_duration(self):
        self.duration = (datetime.datetime(2019, 1, 1, self.end_hour,
                                           self.end_minute, 0) -
                         datetime.datetime(2019, 1, 1, self.start_hour,
                                           self.start_minute, 0))\
            .total_seconds() / 60 / 60

    @api.one
    def _compute_default_name(self):
        self.name = "FTQ, " + str(self.id)

    def approve_shift(self):
        self.shift_status = True

    @api.depends('activity_id')
    @api.one
    def _compute_activity_date(self):
        if self.activity_id:
            self.activity_date = self.activity_id[0].date_start

    @api.model
    def create(self, vals):
        if 'activity_id' in vals:
            vals['activity_code'] = self.env['project.task'].browse(
                vals['activity_id']).code
            vals['activity_date'] = self.env['project.task'].browse(
                vals['activity_id']).date_start
        return super(TaskShiftTimesheet, self).create(vals)

    def _compute_dep(self):
        departments = []
        if 'activity_id' in self._context:
            activity = self.env['project.task'].browse(
                self._context['activity_id'])
            current_employee = self.env['res.users'].browse(
                self._context['uid']).employee_ids[0]
            for child in activity.child_ids:
                if current_employee in child.employee_ids:
                    departments.append(child.department_id.id)
        return departments

    @api.one
    def _compute_function(self):
        services = []
        if 'activity_id' in self._context:
            activity = self.env['project.task'].browse(
                self._context['activity_id'])
            current_employee = self.env['res.users'].browse(
                self._context['uid']).employee_ids[0]
            for child in activity.child_ids:
                if current_employee in child.employee_ids:
                    services.append(child.service_id.id)
        return services
