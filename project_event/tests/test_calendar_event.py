# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import fields
from .common import TestProjectEventCommon
from odoo import exceptions


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

    def test_020_unlink(self):
        task_unlink_test = self.Tasks.create({
            'name': 'Task name for unlink test',
            'activity_task_type': 'task',
            'responsible_id': self.responsible_1.id,
            'partner_id': self.partner_1.id,
            'room_id': self.room_1.id,
            'resource_type': 'room',
            'date_start': fields.Datetime.to_string(datetime.today()),
            'date_end': fields.Datetime.to_string(datetime.today() +
                                                  timedelta(hours=4)),
        })
        res = task_unlink_test.action_option()
        wiz = self.env['reservation.validation.wiz'].browse(res['res_id'])
        wiz.confirm_reservation()
        self.assertEqual(
            len(task_unlink_test.info_calendar_event()),
            1
        )
        with self.assertRaises(exceptions.ValidationError):
            task_unlink_test.info_calendar_event().unlink()
