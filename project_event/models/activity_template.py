# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ActivityTemplate(models.Model):
    """Event Activity Template"""
    _name = "activity.template"
    _description = __doc__

    name = fields.Char(
        string='Name',
    )
    event_template_ids = fields.Many2many(
        comodel_name='event.template',
        relation='event_template_activity_template_rel',
        column1='activity_template_id',
        column2='event_template_id',
        string='Events Templates',
    )
    temp_resp_id = fields.Many2one(
        'res.partner',
        string='Responsible',
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category',
    )
    room_id = fields.Many2one(
        'resource.calendar.room',
        string='Room',
    )
    task_template_ids = fields.Many2many(
        comodel_name='task.template',
        relation='activity_template_task_template_rel',
        column1='activity_template_id',
        column2='task_template_id',
        string='Tasks Templates',
    )
    description = fields.Html(
        string='Description',
    )
    notes = fields.Html(
        string='Notes',
    )

    @api.multi
    def action_clear(self):
        self.ensure_one()
        self.task_template_ids.unlink()

    @api.multi
    def action_initialize(self):
        self.action_clear()
        if self.room_id:
            main_task_template_room_vals = {
                'room_id': self.room_id.id,
                'resource_type': 'room',
                'is_main_task': True,
            }
            self._update_task_template(main_task_template_room_vals)
            for instrument in self.room_id.instruments_ids:
                equipment_task_vals = {
                    'equipment_id': instrument.id,
                    'resource_type': 'equipment',
                }
                self._update_task_template(equipment_task_vals)
        else:
            main_task_template_vals = {
                'is_main_task': True,
            }
            self._update_task_template(main_task_template_vals)

    @api.multi
    def _update_task_template(self, vals):
        vals['name'] = self.name
        vals['activity_template_ids'] = [self.id]
        task_template_vals = {
            'task_template_ids': [(0, 0, vals)],
        }
        self.write(task_template_vals)
