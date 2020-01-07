# @ 2018 Savoir-failre Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
import datetime
from odoo.exceptions import ValidationError


class MoveActivityTasksWizard(models.TransientModel):
    """Wizard Move Activity Tasks"""
    _name = 'move.activity.tasks.wiz'
    _description = __doc__

    activity_id = fields.Many2one(
        'project.task',
        string='Task',
    )
    message = fields.Html(
        string='Message',
    )
    days = fields.Integer(
        string='Days',
    )
    hours = fields.Integer(
        string='Hours',
    )
    minutes = fields.Integer(
        string='Minutes',
    )
    moving_date = fields.Datetime()
    child_ids = fields.One2many('project.task', 'parent_id',
                                string="Tasks",
                                readonly=True,
                                compute="_compute_get_activity_childs",
                                )
    moving_direction = fields.Selection(string='Type',
                                        selection=[
                                            ('before', 'Before'),
                                            ('after', 'After')
                                        ],
                                        default="after")
    moving_type = fields.Selection(string='Type',
                                   selection=[
                                       ('interval', 'Interval moving'),
                                       ('date', 'Date moving')
                                   ],
                                   default="interval")
    move_activity = fields.Boolean(default=True)

    def _send_message_to_subscribers(self, task):
        if not task.is_activity() and task.task_state not in ['draft',
                                                              'postponed',
                                                              'canceled']:
            self.env['mail.message'].create(self.get_message(task))
        elif task.is_activity() and task.task_state not in ['draft',
                                                            'postponed',
                                                            'canceled']:
            self.env['mail.message'].create(self.get_message(task.
                                                             get_main_task()))

    def _compute_get_activity_childs(self):
        tasks = []
        for child in self.activity_id.child_ids:
            if not child.is_main_task:
                tasks.append(child.id)

        self.child_ids = [(6, False, tasks)]

    def _move_tasks_with_interval(self, direction, task):
        task.write({
            'date_start': (datetime.datetime.strptime(task.date_start,
                                                      '%Y-%m-%d %H:%M:%S') +
                           direction * datetime.timedelta(
                days=self.days,
                hours=self.hours,
                minutes=self.minutes)).strftime('%Y-%m-%d %H:%M:%S'),
            'date_end': (datetime.datetime.strptime(task.date_end,
                                                    '%Y-%m-%d %H:%M:%S') +
                         direction * datetime.timedelta(
                days=self.days,
                hours=self.hours,
                minutes=self.minutes)).strftime('%Y-%m-%d %H:%M:%S')
        })
        self._send_message_to_subscribers(task)

    def _move_tasks_to_date(self, task):
        moving_date = datetime.datetime.strptime(self.moving_date,
                                                 '%Y-%m-%d %H:%M:%S')
        date_start = datetime.datetime.strptime(task.date_start,
                                                '%Y-%m-%d %H:%M:%S')
        date_end = datetime.datetime.strptime(task.date_end,
                                              '%Y-%m-%d %H:%M:%S')
        task.write({
            'date_start': datetime.datetime(moving_date.year,
                                            moving_date.month,
                                            moving_date.day,
                                            date_start.hour,
                                            date_start.minute,
                                            date_start.second,
                                            ).strftime('%Y-%m-%d %H:%M:%S'),
            'date_end': datetime.datetime(
                moving_date.year,
                moving_date.month,
                moving_date.day,
                date_end.hour,
                date_end.minute,
                date_end.second,
            ).strftime('%Y-%m-%d %H:%M:%S')
        })
        self._send_message_to_subscribers(task)

    @api.multi
    def confirm_moving(self):
        if self.moving_type == 'interval':
            if self.moving_direction == 'before':
                if self.move_activity:
                    self._move_tasks_with_interval(-1, self.activity_id)
                for child in self.child_ids:
                    if child.moving_checked and not child.is_main_task:
                        self._move_tasks_with_interval(-1, child)
            else:
                if self.move_activity:
                    self._move_tasks_with_interval(1, self.activity_id)
                for child in self.child_ids:
                    if child.moving_checked and not child.is_main_task:
                        self._move_tasks_with_interval(1, child)

        else:
            if self.moving_date:
                if self.move_activity:
                    self._move_tasks_to_date(self.activity_id)
                for child in self.child_ids:
                    self._move_tasks_to_date(child)
            else:
                raise ValidationError(_("You must set a new date!"))

    def get_message(self, task):
        message = '<br>'
        if task.is_activity():
            message += _('Activity: ') + task.name
        elif task.activity_task_type == 'task':
            message += _('Task: ') + task.name
        return {
            'body': message + _(' has been moved to ') + fields.Datetime.
            context_timestamp(self, datetime.datetime.strptime(task.date_start,
                                                               '%Y-%m-%d '
                                                               '%H:%M:%S'))
            .strftime('%Y-%m-%d %H:%M:%S'),
            'channel_ids': [(6, 0, task.message_channel_ids.ids)],
            'email_from': 'Administrator <admin@yourcompany.example.com>',
            'message_type': 'notification',
            'model': 'project.task',
            'partner_ids': [(6, 0, task.message_partner_ids.ids)],
            'record_name': task.name,
            'reply_to': 'Administrator <admin@yourcompany.example.com>',
            'res_id': task.id,
            'subject': task.code
        }
