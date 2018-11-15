# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    category_id = fields.Many2one(
        'task.category',
        string='Category',
        default=lambda self: self.default_category_id(),
    )

    def default_category_id(self):
        return self.env['task.category'].search(
            [],
            order='sequence',
            limit=1
        )
