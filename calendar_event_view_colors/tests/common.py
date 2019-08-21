# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.tests import common


class CalendarTagConfigCommon(common.TransactionCase):

    def setUp(self):
        super(CalendarTagConfigCommon, self).setUp()

        # Usefull models
        self.CalendarTagConfig = self.env['calendar.color.tag.fields']
        self.calendar_event = self.env['calendar.event']
        self.project_task = self.env['project.task']
        self.ir_model = self.env['ir.model']
        self.ir_model_fields = self.env['ir.model.fields']

        model_vals = {
            'name': 'x_calendar.tag',
            'model': 'x_calendar.tag',
        }
        self.model_tag = self.ir_model.create(model_vals)

        # tag_name_field_vals = {
        #     'name': 'x_name',
        #     'model': 'calendar.tag',
        #     'model_id': self.model_tag.id,
        #     'field_description': 'Name',
        #     'ttype': 'char',
        #
        # }
        # self.tag_color_field = self.ir_model_fields.create(
        #     tag_name_field_vals)

        tag_color_field_vals = {
            'name': 'x_color',
            'model': 'calendar.tag',
            'model_id': self.model_tag.id,
            'field_description': 'Color',
            'ttype': 'char',

        }
        self.tag_color_field = self.ir_model_fields.create(
            tag_color_field_vals)

        tag_font_color_field_vals = {
            'name': 'x_font_color',
            'model': 'calendar.tag',
            'model_id': self.model_tag.id,
            'field_description': 'Font Color',
            'ttype': 'selection',
            'selection': '''[('black', 'Black (Default)'), ('white', 'White')]''',

        }
        self.tag_font_color_field = self.ir_model_fields.create(
            tag_font_color_field_vals)

        calendar_event_model_id = self.ir_model.search(
            [('model', '=', 'calendar.event')], limit=1)
        print('model_id', calendar_event_model_id.id)
        # tag_id_field_vals = {
        #     'name': 'x_calendar_tag_id',
        #     'model': 'calendar.event',
        #     'model_id': calendar_event_model_id.id,
        #     'field_description': 'Tag',
        #     'ttype': 'many2one',
        #     'relation': 'calendar.tag',
        # }
        # self.tag_id_field = self.ir_model_fields.create(
        #     tag_id_field_vals)

        # self.calendar_tag = self.env['calendar.tag']
        self.calendar_tag1 = self.model_tag.create(
            {
                'name': 'Tag1',
                'x_color': '#114789',
                'x_font_color': 'white',
            }
        )

