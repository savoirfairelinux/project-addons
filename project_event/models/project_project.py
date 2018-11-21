# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'mail.thread']

    code = fields.Char(
        string='Number',
    )
    responsible_id = fields.Many2one(
        'res.partner',
        string='Responsible',
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
    )
    project_type = fields.Selection(
        [
            ('event', 'Event'),
            ('project', 'Project'),
        ],
        string='Type',
        default='project',
    )
    notes = fields.Html(
        string='Notes',
        track_visibility='onchange',
    )
    description = fields.Html(string='Description')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('option', 'Option'),
            ('accepted', 'Accepted'),
            ('postponed', 'Postponed'),
            ('canceled', 'Canceled')
        ],
        string='State',
        default='draft',
        track_visibility='onchange',
    )
    event_log_count = fields.Integer(
        string='Event Logs',
        compute='_compute_event_log_count',
    )

    def _compute_event_log_count(self):
        for rec in self:
            rec.event_log_count = self.env['auditlog.log'].search_count([
                ('model_id', '=', self.env.ref(
                    'project.model_project_project').id),
                ('res_id', '=', rec.id)
            ])

    @api.multi
    def write(self, vals):
        super(Project, self).write(vals)
        if self.project_type == 'event':
            for activitiy in self.task_ids:
                activitiy.write({
                    'responsible_id': self.responsible_id.id,
                    'partner_id': self.partner_id.id
                })
                for task in activitiy.child_ids:
                    task.write({
                        'responsible_id': self.responsible_id.id,
                        'partner_id': self.partner_id.id
                    })

    @api.multi
    def action_cancel(self):
        if self.state == 'accepted':
            self.send_message('canceled')
        for activity in self.task_ids:
                activity.action_cancel()
        self.write({'state': 'canceled'})

    @api.multi
    def action_accept(self):
        if self.state in ['draft', 'option', 'postponed', 'canceled']:
            self.send_message('accepted')
            for activity in self.task_ids:
                activity.action_accept()
        self.write({'state': 'accepted'})

    @api.multi
    def action_option(self):
        if self.state == 'accepted':
            self.send_message('option')
        res = ''
        for activity in self.task_ids:
            res += activity.get_booked_resources()
        if res != '':
            res = _('The Following resources are already booked:<br>') + res
        message = _('Please Confirm your reservation.<br>') + res + _(
            'Do you want to continue?')
        new_wizard = self.env['reservation.validation.wiz'].create(
            {
                'event_id': self.id,
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
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_postpone(self):
        if self.state == 'accepted':
            self.send_message('postponed')
        for activity in self.task_ids:
                activity.action_postpone()
        self.write({'state': 'postponed'})

    @api.model
    def create(self, vals):
        if 'project_type' in vals:
            if vals['project_type'] == 'event':
                vals['code'] = self.env['ir.sequence'] \
                    .next_by_code('project.project')
        return super(Project, self).create(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name),
                      ('code', operator, name)]
        return super(Project, self).search(
            domain + args, limit=limit).name_get()

    def get_message_body(self, action):
        switcher = {
            'draft': ' ',
            'option': _('The following is Optional and \
                        appears as crosshatched on your calendar'),
            'accepted': _('The following is approved'),
            'postponed': _('The following is postponed \
                        and no longer appear on your calendars'),
            'canceled': _('The following is canceled\
                         and no longer on your calendars')
        }
        return switcher.get(action)

    def get_message(self, action):
        message = '<br>'
        message += _('Event: <br>') + self.name + '<br>'
        for activity in self.task_ids:
            message += _('Activity: ') + activity.name + _('<br> Tasks: ')
            for index_task, task in enumerate(activity.child_ids):
                message += task.name
                if index_task < len(activity.child_ids) - 1:
                    message += ', '
                else:
                    message += '<br>'
        return {
            'body': self.get_message_body(action) + message,
            'channel_ids': [(6, 0, [self.env.ref
                            ('project.mail_channel_project_task_event').id])],
            'email_from': 'Administrator <admin@yourcompany.example.com>',
            'message_type': 'notification',
            'model': 'project.project',
            'partner_ids': [(6, 0, [self.responsible_id.id])],
            'record_name': self.name,
            'reply_to': 'Administrator <admin@yourcompany.example.com>',
            'res_id': self.id,
            'subject': self.code
        }

    def send_message(self, action):
        self.env['mail.message'].create(self.get_message(action))
