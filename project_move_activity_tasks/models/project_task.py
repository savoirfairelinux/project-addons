# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Task(models.Model):
    _inherit = ['project.task']

    moving_checked = fields.Boolean(
        'Checked',
        default=True
    )

    @api.multi
    def get_move_activity_tasks_wizard(self):
        self.ensure_one()
        message = 'Select tasks to move and choose interval or date'
        for child in self.child_ids:
            child.moving_checked = True
        new_wizard = self.env['move.activity.tasks.wiz'].create(
            {
                'activity_id': self.id,
                'message': message,
            }
        )
        return {
            'name': 'Move activity tasks',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'move.activity.tasks.wiz',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    @api.multi
    def action_toggle_checkbox(self):
        if self.moving_checked:
            self.moving_checked = False
        else:
            self.moving_checked = True
        return {
            "type": "ir.actions.do_nothing",
        }
