# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class ProjectEventWizard(models.TransientModel):
    """Wizard Event Creation from Template"""
    _name = 'project.event.wizard'
    _description = __doc__

    template_id = fields.Many2one(
        'event.template',
        string='Event Template',
    )
    name = fields.Char(
        string='Event Title',
    )
    event_resp_id = fields.Many2one(
        'res.partner',
        string='Responsible',
    )
    event_notes = fields.Text(
        string='Notes',
    )
    activity_ids = fields.One2many(
        'project.activity.wizard',
        'event_wizard_id',
        string='Activities to Edit',
    )
    task_line_ids = fields.One2many(
        'project.task.wizard',
        'event_wizard_id',
        string='Tasks to Edit',
    )

    @api.multi
    def add_activities(self):
        self.ensure_one()
        template = self.env['event.template'].browse(self.template_id.id)
        view = self.env.ref(
            'project_event.view_project_activity_wizard')
        for act in template.activity_template_ids:
            activity_vals = {
                'template_id': act.id,
                'name': act.name,
                'event_wizard_id': self.id,
                'room_id': act.room_id.id,
                'activity_resp_id': act.temp_resp_id.id,
                'activity_category_id': act.activity_category_id.id,
                'notes': act.notes,
            }
            self.env['project.activity.wizard'].create(activity_vals)

        return {
            'name': _('Activities Wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'views': [(view.id, 'form')],
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

    @api.multi
    def add_tasks(self):
        self.ensure_one()
        activities = self.activity_ids
        view = self.env.ref(
            'project_event.view_project_task_wizard')
        for act in activities:
            for task in act.template_id.task_template_ids:
                task_vals = {
                    'event_wizard_id': self.id,
                    'template_id': task.id,
                    'activity_wiz_id': act.id,
                    'task_name': task.name,
                    'task_resp_id': task.temp_resp_id.id,
                    'task_category_id': task.task_category_id.id,
                    'resource_type': task.resource_type,
                    'equipment_id': task.equipment_id.id,
                    'room_id': task.room_id.id,
                    'department_id': task.department_id.id,
                    'duration': task.duration,
                    'start_time': task.start_time,
                    'notes': task.notes,
                }
                self.env['project.task.wizard'].create(task_vals)

        return {
            'name': _('Tasks Wizard'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'views': [(view.id, 'form')],
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

    @api.multi
    def create_event_from_template(self):
        self.ensure_one()
        event_vals = {
            'name': self.name,
            'responsible_id': self.event_resp_id.id,
            'notes': self.event_notes,
            'project_type': 'event',
        }
        event = self.env['project.project'].create(event_vals)
        for act in self.activity_ids:
            tasks = self.env['project.task.wizard'].search([
                ('event_wizard_id', '=', self.id),
                ('activity_wiz_id', '=', act.id),
            ])
            activity_vals = {
                'name': act.name,
                'project_id': event.id,
                'responsible_id': act.activity_resp_id.id,
                'activity_category_id': act.activity_category_id.id,
                'activity_task_type': 'activity',
                'room_id': act.room_id.id,
                'notes': act.notes,
                'child_ids': [
                    (0,
                     0,
                     {
                         'name': task.task_name,
                         'activity_task_type': 'task',
                         'task_responsible_id': task.task_resp_id.id,
                         'task_category_id': task.task_category_id.id,
                         'department_id': task.department_id.id,
                         'resource_type': task.resource_type,
                         'equipment_id': task.equipment_id.id,
                         'room_id': task.room_id.id,
                         'notes': task.notes,
                     }
                     ) for task in tasks],
            }
            self.env['project.task'].create(activity_vals)

    @api.onchange('template_id')
    def _onchange_template_id(self):
        template = self.env['event.template'].browse(self.template_id.id)
        self.name = template.name
        self.event_resp_id = template.temp_resp_id
        self.event_notes = template.notes
