# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
import datetime


class TaskShiftTimesheet(models.Model):
    _name = 'shift.timesheet'

    activity_id = fields.Many2one(
        'project.task',
        track_visibility='onchange',
        domain="[('activity_task_type', 'in', ['activity'])]",
    )
    activity_code = fields.Char(
        related='activity_id.code',
    )
    activity_date = fields.Datetime(
        related='activity_id.date_start',
    )
    department = fields.Many2one(
        'hr.department',
        track_visibility='onchange',
    )
    function = fields.Char(string='Function')
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        track_visibility='onchange',
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
    duration = fields.Integer(
        string='Duration',
        compute='_compute_duration',
    )
    shift_status = fields.Boolean(
        default=False
    )

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
            .total_seconds()/60/60

    def approve_shift(self):
        self.shift_status = True
