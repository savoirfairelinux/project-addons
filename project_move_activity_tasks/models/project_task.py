# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class Task(models.Model):
    _inherit = ['project.task']

    @api.multi
    def get_move_activity_tasks_wizard(self):
        self.ensure_one()
        message = 'Move activity taks'
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