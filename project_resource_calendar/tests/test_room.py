# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCalendarEventCommon


class TestRoom(TestCalendarEventCommon):

    def setUp(self):
        super(TestRoom, self).setUp()
        self.check_record_count = 2
        self.model_name = 'project_resource_calendar.' \
                          'model_resource_calendar_room'

        self.room = self.Rooms.create({
            'name': 'Test Room for Auditlog Testing',
            'resource_type': 'room',
            'allow_double_book': True,
        })

        self.AuditLogObj = self.env['auditlog.log']
        self.AuditLogObj.create({
            'model_id': self.env.ref(
                self.model_name).id,
            'res_id': self.room.id,
        })

    def test_010_compute_room_log_count(self):
        self.assertEqual(self.room.room_log_count, self.check_record_count)
