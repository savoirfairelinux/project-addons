# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api



class CalendarEventReport(models.AbstractModel):
    _name = 'report.project_resource_calendar.calendar_event_report_view'

    @api.model
    def get_report_values(self, docids, data=None):
        import ipdb; ipdb.set_trace()
      
        return docs
