# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ProjectTaskType(models.Model):
    _inherit = ['project.task.type']

    is_reservation_trigger = fields.Boolean(string='Trigger resource reservation',
        help='Do reservation when passing to this stage')


    # def _get_default_project_ids(self):
    #     default_project_id = self.env.context.get('default_project_id')
    #     return [default_project_id] if default_project_id else None

    # name = fields.Char(string='Stage Name', required=True, translate=True)
    # description = fields.Text(translate=True)
    # sequence = fields.Integer(default=1)
    # project_ids = fields.Many2many('project.project', 'project_task_type_rel', 'type_id', 'project_id', string='Projects',
    #     default=_get_default_project_ids)
    # legend_priority = fields.Char(
    #     string='Starred Explanation', translate=True,
    #     help='Explanation text to help users using the star on tasks or issues in this stage.')
    # legend_blocked = fields.Char(
    #     'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
    #     help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    # legend_done = fields.Char(
    #     'Green Kanban Label', default=lambda s: _('Ready for Next Stage'), translate=True, required=True,
    #     help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    # legend_normal = fields.Char(
    #     'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
    #     help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    # mail_template_id = fields.Many2one(
    #     'mail.template',
    #     string='Email Template',
    #     domain=[('model', '=', 'project.task')],
    #     help="If set an email will be sent to the customer when the task or issue reaches this step.")
    # fold = fields.Boolean(string='Folded in Kanban',
    #     help='This stage is folded in the kanban view when there are no records in that stage to display.')

