# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    category_id = fields.Many2one(
        'task.category',
        string='Category',
        default=lambda self: self.env['task.category'].search([('is_default', '=', True)])
    )

    color = fields.Char(related='category_id.color')
