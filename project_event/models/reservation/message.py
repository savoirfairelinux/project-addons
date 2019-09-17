

from odoo import fields, models, api, _

MSG_RES = 'The following resources are already booked:<br>'
MSG_CONFIRM = 'Please confirm your reservation.<br>'
MSG_CONTINUE = 'Do you want to continue?'

class Message(models.TransientModel):
    _name = 'project.task.message'

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

    def get_message(self, project_task, action):
        message = '<br>'
        if project_task.is_activity():
            message += _('Activity: <br>') + project_task.name + '<br>'
            message += _('Tasks: <br>')
            for index_task, task in enumerate(project_task.child_ids):
                message += task.name
                if index_task < len(project_task.child_ids) - 1:
                    message += ', '
        elif project_task.activity_task_type == 'task':
            message += _('Task: <br>') + project_task.name
        return {
            'body': self.get_message_body_task(action) + message,
            'channel_ids': [(6, 0, project_task.message_channel_ids.ids)],
            'email_from': 'Administrator <admin@yourcompany.example.com>',
            'message_type': 'notification',
            'model': 'project.task',
            'partner_ids': [(6, 0, project_task.message_partner_ids.ids)],
            'record_name': project_task.name,
            'reply_to': 'Administrator <admin@yourcompany.example.com>',
            'res_id': project_task.id,
            'subject': project_task.code
        }

    def send_message(self, action):
        self.env['mail.message'].create(self.get_message(action))
