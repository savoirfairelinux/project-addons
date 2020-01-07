# Copyright 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Room(models.Model):
    _inherit = ['resource.resource']
    _name = 'resource.calendar.room'
    _order = 'name'

    room_code = fields.Char(
        string='Room ID',
    )
    capacity = fields.Integer(
        string='Capacity',
    )
    floor = fields.Char(
        string='Floor',
    )
    room_type_id = fields.Many2one(
        string='Room Type',
        comodel_name='resource.calendar.room.type',
        ondelete='set null',
    )
    department_id = fields.Many2one(
        string='Department',
        comodel_name='hr.department',
        ondelete='set null',
    )
    instruments_ids = fields.One2many(
        'resource.calendar.instrument',
        'room_id',
        string='Instruments/Equipements',
    )
    miscellaneous = fields.Many2many(
        string='Miscellaneous',
        comodel_name='resource.calendar.miscellaneous',
    )
    room_log_count = fields.Integer(
        string='Room Logs',
        compute='_compute_room_log_count',
    )
    tag_ids = fields.Many2many(
        'hr.employee.category', 'room_category_rel',
        'room_id', 'category_id',
        string='Employee Tags'
    )
    group_ids = fields.Many2many(
        'res.groups', 'room_group_rel',
        'room_id', 'group_id',
        string='Groups'
    )

    def _compute_room_log_count(self):
        room = 'project_resource_calendar.model_resource_calendar_room'
        for rec in self:
            rec.room_log_count = self.env['auditlog.log'].search_count([
                ('model_id', '=', self.env.ref(
                    room).id),
                ('res_id', '=', rec.id)
            ])

    @api.model
    def create(self, values):
        """
            Create a new record for a model Room
            @param values: provides a data for new record
            @return: returns a id of new record
        """
        values['resource_type'] = 'room'
        result = super().create(values)
        return result
