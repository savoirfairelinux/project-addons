# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import datetime, timedelta
from odoo import fields
from .common import CalendarTagConfigCommon


class TestCalendarEvent(CalendarTagConfigCommon):

    def setUp(self):
        super(TestCalendarEvent, self).setUp()
        self.Calendar = self.env['calendar.event']
        self.vals = {
            'name': 'Calendar Event 1',
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
            'tag_id': self.calendar_tag1,
        }
        self.calendar_event1 = self.Calendar.create(self.vals)

    def test_010_get_color_fields(self, model_name):
        print ('hello')


    def test_020_get_calendar_color_fields(self, model_name):
        print('hello 2')

    def test_030_get_calendar_tag_values(self, model_name,record_id):
        print('hello 3')

    def test_040_check_fiel_exist(self):
        print('hello 4')
        tag1 = self.calendar_tag.browse(1)
        print('tag1', tag1.name)
        ev1 = self.calendar_event1.search([('name', '=', 'Calendar Event 1')])
        print('ev1', ev1.name)
        print('ev1', ev1.tag_id.name)


