# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


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
    event_partner_id = fields.Many2one(
        'res.partner',
        string='Client',
    )
    event_sector_id = fields.Many2one(
        'res.partner.sector',
        string='Faculty Sector',
    )
    event_notes = fields.Html(
        string='Notes',
    )
    event_description = fields.Html(
        string='Description',
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
    general_room_id = fields.Many2one(
        'resource.calendar.room',
        string='General Room',
    )

    @api.multi
    def add_flex_activities(self):
        self.ensure_one()
        template = self.env['event.template'].browse(self.template_id.id)
        view = self.env.ref(
            'project_event_template.view_project_activity_wizard')
        for act in template.activity_template_ids:
            activity_vals = {
                'template_id': act.id,
                'name': act.name,
                'event_wizard_id': self.id,
                'room_id': act.room_id.id,
                'department_id': act.department_id.id,
                'service_id': act.service_id.id,
                'duration': act.duration,
                'activity_resp_id': self.event_resp_id and
                self.event_resp_id.id or act.temp_resp_id.id,
                'activity_partner_id': self.event_partner_id and
                self.event_partner_id.id or False,
                'activity_sector_id': self.event_sector_id and
                self.event_sector_id.id or False,
                'category_id': act.category_id.id,
                'description': act.description,
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
    def add_flexible_tasks(self):
        self.ensure_one()
        activities = self.activity_ids
        view = self.env.ref(
            'project_event_template.view_project_task_wizard')
        for act in activities:
            for task in act.template_id.task_template_ids:
                task_vals = {
                    'event_wizard_id': self.id,
                    'template_id': task.id,
                    'activity_wiz_id': act.id,
                    'task_name': task.name,
                    'task_resp_id': act.activity_resp_id and
                    act.activity_resp_id.id or task.temp_resp_id.id,
                    'task_partner_id': act.activity_partner_id and
                    act.activity_partner_id.id or False,
                    'task_sector_id': act.activity_sector_id and
                    act.activity_sector_id.id or False,
                    'category_id': task.category_id.id,
                    'resource_type': task.resource_type,
                    'equipment_id': task.equipment_id.id,
                    'room_id': (
                        act.room_id and act.room_id.id or task.room_id.id
                    ) if task.resource_type == 'room' else False,
                    'service_id': task.service_id.id,
                    'department_id': task.department_id.id,
                    'employee_ids': [(4, e.id) for e in task.employee_ids],
                    'duration': task.duration,
                    'start_time': task.start_time,
                    'description': task.description,
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
            'context': dict(self.env.context or {}),
        }

    @api.multi
    def create_event_from_template(self):
        self.ensure_one()
        event_vals = {
            'name': self.name,
            'responsible_id': self.event_resp_id.id,
            'partner_id': self.event_partner_id.id,
            'client_type': self.event_partner_id.tag_id.client_type.id,
            'sector_id': self.event_sector_id.id,
            'notes': self.event_notes,
            'project_type': 'event',
            'description': self.event_description,
        }
        event = self.env['project.project'].create(event_vals)
        for act in self.activity_ids:
            tasks = self.env['project.task.wizard'].search([
                ('activity_wiz_id', '=', act.id),
            ])
            activity_vals = {
                'name': act.name,
                'project_id': event.id,
                'responsible_id': act.activity_resp_id.id,
                'partner_id': act.activity_partner_id.id,
                'client_type': self.event_partner_id.tag_id.client_type.id,
                'sector_id': act.activity_sector_id.id,
                'category_id': act.category_id.id,
                'activity_task_type': 'activity',
                'room_id': act.room_id.id,
                'department_id': act.department_id.id,
                'service_id': act.service_id.id,
                'date_start': act.date_start,
                'date_end': fields.Datetime.from_string(
                    act.date_start) + relativedelta(minutes=act.duration),
                'description': act.description,
                'notes': act.notes,
                'child_ids': [
                    (0,
                     0,
                     {
                         'name': task.task_name,
                         'activity_task_type': 'task',
                         'responsible_id': task.task_resp_id.id,
                         'partner_id': task.task_partner_id.id,
                         'client_type': self.event_partner_id.tag_id
                            .client_type.id,
                         'sector_id': task.task_sector_id.id,
                         'category_id': task.category_id.id,
                         'department_id': task.department_id.id,
                         'employee_ids':
                         [(4, e.id) for e in task.employee_ids],
                         'resource_type': task.resource_type,
                         'equipment_id': task.equipment_id.id,
                         'room_id': task.room_id.id,
                         'service_id': task.service_id.id,
                         'date_start': (
                             fields.Datetime.from_string(
                                 act.date_start) + relativedelta(
                                 minutes=task.start_time)
                         ),
                         'date_end': (
                             fields.Datetime.from_string(
                                 act.date_start) + relativedelta(
                                 minutes=task.start_time + task.duration)
                         ),
                         'notes': task.notes,
                         'description': task.description,
                     }
                     ) for task in tasks],
            }
            self.env['project.task'].create(activity_vals)

    @api.onchange('template_id')
    def _onchange_template_id(self):
        template = self.env['event.template'].browse(self.template_id.id)
        self.name = template.name
        self.event_resp_id = template.temp_resp_id
        self.event_description = template.description
        self.event_notes = template.notes

    @api.onchange('general_room_id')
    def _onchange_general_room_id(self):
        if self.general_room_id:
            for act in self.task_line_ids:
                if act.resource_type == 'room':
                    act.room_id = self.general_room_id
