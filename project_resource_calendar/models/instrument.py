# Copyright 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Instrument(models.Model):
    """Resource Calendar Instrument"""
    _name = 'resource.calendar.instrument'
    _inherit = ['resource.resource']
    _description = __doc__

    sku = fields.Char(
        string='SKU',
    )
    room_id = fields.Many2one(
        'resource.calendar.room',
        string='Room',
    )
    category_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('consumable', 'Consumable'),
        ('instrument', 'Instrument'),
    ],
        string='Type',
        index=True,
        default='instrument',
    )
    instrument_log_count = fields.Integer(
        string='Calendar Logs',
        compute='_compute_instrument_log_count',
    )

    def _compute_instrument_log_count(self):
        insmnt = 'project_resource_calendar.model_resource_calendar_instrument'
        for rec in self:
            rec.instrument_log_count = self.env['auditlog.log'].search_count([
                ('model_id', '=', self.env.ref(
                    insmnt).id),
                ('res_id', '=', rec.id)
            ])
