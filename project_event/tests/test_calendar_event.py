# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import datetime, timedelta
from odoo import fields
from odoo.addons.project_event.tests.common import TestProjectEventCommon


class TestCalendarEvent(TestProjectEventCommon):

    def setUp(self):
        super(TestCalendarEvent, self).setUp()
        self.Calendar = self.env['calendar.event']
        self.vals = {
            'name': 'Calendar Event 1',
            'start': fields.Datetime.to_string(datetime.today()),
            'stop': fields.Datetime.to_string(datetime.today() +
                                              timedelta(hours=4)),
        }
        self.calendar_event = self.Calendar.create(self.vals)

    def test_010_calendar_event_change_client_id_with_client_tag(self):
        self.calendar_event.write({'client_id': self.partner_2.id})
        self.calendar_event._onchange_client_id()
        self.assertEqual(
            self.partner_2.tag_id.client_type,
            self.calendar_event.client_type
        )
