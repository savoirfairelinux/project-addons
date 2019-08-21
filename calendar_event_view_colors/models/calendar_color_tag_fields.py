# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class CalendarColorTagFields(models.Model):
    _name = 'calendar.color.tag.fields'

    name = fields.Char(
        string='Description',
        required=True,
    )
    model_id = fields.Many2one(
        string='Model',
        comodel_name='ir.model',
        required=True,
        help="The model to which the tag rule applies."
    )
    model_name = fields.Char(
        related='model_id.model',
        readonly=True,
    )
    tag_field_id = fields.Char(
        string='Tag Field',
    )
    font_color_field = fields.Char(
        string='Font Color Field',
    )
    color_field = fields.Char(
        string='Color Field',
    )
    calendar_font_color_field = fields.Char(
        string='Calendar Font Color Field',
    )
    calendar_color_field = fields.Char(
        string='Calendar Color Field',
    )
    calendar_state_field = fields.Char(
        string='Calendar State Field',
    )

    @api.model
    def get_color_fields(self, model_name):
        print('hello from get color fields')
        tag_field_id = ''
        color_field = ''
        font_color_field = ''
        calendar_tag = self.env['calendar.color.tag.fields'].search(
            [('model_name', '=', model_name)], limit=1)
        print('aa', calendar_tag.tag_field_id)
        if calendar_tag:
            tag_field_id = calendar_tag.tag_field_id
            color_field = calendar_tag.color_field
            font_color_field = calendar_tag.font_color_field
        return tag_field_id, color_field, font_color_field

    @api.model
    def get_calendar_color_fields(self, model_name):
        print('hello from get calendar color fields')
        calendar_state_field = ''
        calendar_color_field = ''
        calendar_font_color_field = ''
        calendar_tag = self.env['calendar.color.tag.fields'].search(
            [('model_name', '=', model_name)], limit=1)
        print('aa', calendar_tag.tag_field_id)
        if calendar_tag:
            calendar_color_field = calendar_tag.calendar_color_field
            calendar_font_color_field = calendar_tag.calendar_font_color_field
            calendar_state_field = calendar_tag.calendar_state_field
        return calendar_color_field, calendar_font_color_field, calendar_state_field

    @api.model
    def get_calendar_tag_values(self, model_name, record_id):
        print('hello from get_calendar_tag_values')
        tag_values = {'color': '', 'font_color': '', 'state': ''}
        calendar_tag = self.env['calendar.color.tag.fields'].search(
            [('model_name', '=', model_name)], limit=1)
        tag_obj = self.env[model_name]
        aa = tag_obj.browse(record_id)
        if aa:
            tag_values['color'] = aa[calendar_tag['color_field']]
            tag_values['font_color'] = aa[calendar_tag['font_color_field']]
            tag_values['state'] = aa[calendar_tag['state']]
        return tag_values

