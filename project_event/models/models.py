# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api
from odoo.osv.orm import BaseModel


@api.multi
def get_formview_id(self, access_uid=None):
    """ Return an view id to open the document ``self`` with. This method is
        meant to be overridden in addons that want to give specific view ids
        for example.

        Optional access_uid holds the user that would access the form view
        id different from the current environment user.
    """
    if self._name == 'project.task':
        if self.activity_task_type == 'task':
            return self.env.ref('project_event.project_event_task_form').id
    return False


BaseModel.get_formview_id = get_formview_id
