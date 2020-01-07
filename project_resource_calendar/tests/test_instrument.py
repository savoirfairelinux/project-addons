# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCalendarEventCommon


class TestInstrument(TestCalendarEventCommon):

    def setUp(self):
        super(TestInstrument, self).setUp()
        self.check_record_count = 2
        self.model_name = 'project_resource_calendar.' \
                          'model_resource_calendar_instrument'

        self.room_info = self.Rooms.create({
            'name': 'Test Room for Auditlog Testing',
            'resource_type': 'room',
            'allow_double_book': True,
        })
        self.instrument = self.Instruments.create({
            'name': 'Test Instrument for Auditlog Testing',
            'resource_type': 'material',
            'room_id': self.room_info.id,
            'allow_double_book': True,
        })

        self.AuditLogObj = self.env['auditlog.log']
        self.AuditLogObj.create({
            'model_id': self.env.ref(self.model_name).id,
            'res_id': self.instrument.id,
        })

    def test_010_compute_instrument_log_count(self):
        self.assertEqual(
            self.instrument.instrument_log_count,
            self.check_record_count)
