# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.addons.project_resource_calendar.tests.common import TestCalendarEventCommon


class TestRoom(TestCalendarEventCommon):

    def setUp(self):
        super(TestRoom, self).setUp()
        self.Rooms = self.env['resource.calendar.room']
        self.calendar_1 = self.Rooms.create({
            'name': 'Test Calendar 1',
        })
        self.AuditLogObj = self.env['auditlog.log']
        self.AuditLogObj.create({
            'model_id': self.env.ref(
                'project_resource_calendar.model_resource_calendar_room').id,
            'res_id': self.calendar_1.id,
        })

    def test_010_compute_room_log_count(self):
        self.assertEqual(self.calendar_1.room_log_count, 2)
