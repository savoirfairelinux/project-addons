# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


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
    child_ids = fields.One2many('project.task', 'parent_id',
                                string="Tasks",
                                context={'active_test': False})

#    @api.multi
#    def confirm_reservation(self):
#        if self.task_id:
#            self.task_id.do_reservation()
#        else:
#            for activity in self.event_id.task_ids:
#                activity.do_reservation()
#            if self.event_id.state == 'accepted':
#                self.event_id.send_message('option')
#            self.event_id.write({'state': 'option'})
