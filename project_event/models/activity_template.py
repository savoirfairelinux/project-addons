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
    event_template_id = fields.Many2one(
        'event.template',
        default=lambda self: self.env.context.get(
            'default_event_template_id'),
        string='Event Template',
    )
    temp_resp_id = fields.Many2one(
        'res.partner',
        related='event_template_id.temp_resp_id',
        readonly=True,
        string='Responsible',
        store=True,
    )
    activity_category_id = fields.Many2one(
        'task.category',
        string='Category',
    )
    room_id = fields.Many2one(
        'resource.calendar.room',
        string='Room',
    )
    task_template_ids = fields.One2many(
        'task.template',
        'activity_template_id',
        string='Tasks Template',
    )
    notes = fields.Text(
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
            task = {
                'room_id': self.room_id.id,
                'resource_type': 'room',
                'name': self.name,
                'activity_template_id': self.id,
            }
            self.env['task.template'].create(task)
            for instrument in self.room_id.instruments_ids:
                equipment = {
                    'equipment_id': instrument.id,
                    'resource_type': 'equipment',
                    'name': instrument.name,
                    'activity_template_id': self.id,
                }
                vals = {
                    'task_template_ids': [(0, 0, equipment)],
                }
                self.write(vals)
        else:
            main_task = {
                'name': self.name,
                'activity_template_id': self.id,
            }
            self.env['task.template'].create(main_task)
