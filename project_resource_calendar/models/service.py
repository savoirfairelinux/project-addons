# Copyright 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Service(models.Model):
    _inherit = ['resource.resource']
    _name = 'resource.calendar.service'
    _order = 'name'

    service_log_count = fields.Integer(
        string='Service Logs',
        compute='_compute_service_log_count',
    )

    def _compute_service_log_count(self):
        service = 'project_resource_calendar.model_resource_calendar_service'
        for rec in self:
            rec.service_log_count = self.env['auditlog.log'].search_count([
                ('model_id', '=', self.env.ref(
                    service).id),
                ('res_id', '=', rec.id)
            ])
