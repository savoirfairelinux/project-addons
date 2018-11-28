# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ReservationValidationWiz(models.TransientModel):
    """Wizard Reservation Confirmation"""
    _name = 'reservation.validation.wiz'
    _description = __doc__

    task_id = fields.Many2one(
        'project.task',
        string='Task',
    )
    event_id = fields.Many2one(
        'project.project',
        string='Event',
    )
    message = fields.Html(
        string='Message',
    )
    action = fields.Selection(
        [
            ('option', 'Option'),
            ('request', 'Request'),
            ('accept', 'Accept'),
        ],
        string='Action',
    )

    @api.multi
    def confirm_reservation(self):
        if self.task_id:
            self.task_id.do_reservation()
        else:
            for activity in self.event_id.task_ids:
                activity.do_reservation()
            self.event_id.write({'state': 'option'})

    @api.multi
    def confirm_request_reservation(self):
        if self.task_id:
            task = self.task_id
            task.draft_resources_reservation()
            if task.activity_task_type == 'task' and task.task_state in [
                    'draft', 'option', 'postponed', 'canceled']:
                task.send_message('requested')
            task.open_resources_reservation()
            task.write({'task_state': 'requested'})

    @api.multi
    def confirm_accept_reservation(self):
        if self.task_id:
            if self.task_id.activity_task_type == 'activity':
                if self.task_id.task_state in ['draft', 'option', 'postponed',
                                               'canceled']:
                    for child in self.task_id.child_ids:
                        self.child_reservation(child)
                    self.task_id.send_message('requested')
            self.task_id.open_resources_reservation()
            self.task_id.write({'task_state': 'accepted'})
        else:
            for activity in self.event_id.task_ids:
                if activity.task_state in ['draft', 'option', 'postponed',
                                           'canceled']:
                    for child in activity.child_ids:
                        self.child_reservation(child)
                    activity.send_message('requested')
                activity.open_resources_reservation()
                activity.write({'task_state': 'accepted'})
            self.event_id.write({'state': 'accepted'})

    def child_reservation(self, child):
        child.draft_resources_reservation()
        if child.task_state in ['draft', 'option', 'postponed',
                                'canceled']:
            child.send_message('requested')
        child.open_resources_reservation()
        child.write({'task_state': 'requested'})
