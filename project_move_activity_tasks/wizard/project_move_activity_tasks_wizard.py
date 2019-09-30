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
    moving_date = fields.Datetime(
        string='Moving date',
        default=None,
        index=True,
        copy=False,
    )
    child_ids = fields.One2many('project.task', 'parent_id',
                                string="Tasks",
                                readonly=True,
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

    @api.multi
    def confirm_moving(self):
        print('Test')
