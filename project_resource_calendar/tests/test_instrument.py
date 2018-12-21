# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.addons.project_resource_calendar.tests.common import TestCalendarEventCommon


class TestInstrument(TestCalendarEventCommon):

    def setUp(self):
        super(TestInstrument, self).setUp()
        self.Instruments = self.env['resource.calendar.instrument']
        self.calendar_1 = self.Instruments.create({
            'name': 'Test Calendar 1',
        })

        self.AuditLogObj = self.env['auditlog.log']
        self.AuditLogObj.create({
            'model_id': self.env.ref('project_resource_calendar.'
                                     'model_resource_calendar_instrument').id,
            'res_id': self.calendar_1.id,
        })

    def test_001_compute_instrument_log_count(self):
        self.assertEqual(self.calendar_1.instrument_log_count, 2)
