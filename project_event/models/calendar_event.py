# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def default_category_id(self):
        return self.env['task.category'].search(
            [],
            order='sequence',
            limit=1
        )

    category_id = fields.Many2one(
        'task.category',
        string='Category',
        default=default_category_id,
    )
