# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    category_id = fields.Many2one(
        'task.category',
        string='Category',
        default=lambda self: self.env['task.category'].search(
            [('is_default', '=', True)])
    )
    sector_id = fields.Many2one(
        'res.partner.sector',
        string='Faculty Sector',
    )
    client_type = fields.Many2one(
        'res.partner.category.type',
        string='Client Type',
    )
    color = fields.Char(related='category_id.color')
    font_color = fields.Selection([
        ('black', 'Black (Default)'),
        ('white', 'White')],
        related='category_id.font_color')
    client_tag = fields.Many2one(
        string='Client Tag',
        related='client_id.tag_id'
    )

    @api.onchange('client_id')
    def _onchange_client_id(self):
        super(CalendarEvent, self)._onchange_client_id()
        if not self.is_task_event and self.client_id:
            self.client_type = self.client_tag.client_type
