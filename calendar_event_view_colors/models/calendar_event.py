# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    category_id = fields.Many2one(
        'task.category',
        string='Category',
        default=lambda self: self.env['task.category'].search(
            [('is_default', '=', True)])
    )
    color = fields.Char(related='category_id.color')
    font_color = fields.Selection([
        ('black', 'Black (Default)'),
        ('white', 'White')],
        related='category_id.font_color')

    color2 = fields.Char(compute='_compute_color_font_tag', string='Color')
    font_color2 = fields.Char(compute='_compute_color_font_tag',
                                  string='Font Color')

    @api.one
    def _compute_color_font_tag(self):
        model_name = 'calendar.event'
        tags_obj = self.env['calendar.color.tag.fields']
        tag_field, tag_color, tag_font_color = tags_obj.get_color_fields(
            model_name)
        self.color2, self.font_color2 = self.get_tag_color(tag_field, tag_color, tag_font_color)

    def get_tag_color(self, tag_field, tag_color, tag_font_color):
        fields = self.env['calendar.event']._fields
        if tag_field in fields:
            aa = self.env['calendar.event'].browse(self.id)
            return aa[0][tag_field][tag_color], aa[0][tag_field][tag_font_color]
        return False, False
