# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.osv.orm import BaseModel
from lxml import etree
import itertools


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
        elif self.activity_task_type == 'activity':
            return self.env.ref('project_event.project_event_activity_form').id
    return False


BaseModel.get_formview_id = get_formview_id


@api.model
def fields_view_get(
        self,
        view_id=None,
        view_type='form',
        toolbar=False,
        submenu=False):
    """ fields_view_get([view_id | view_type='form'])

    Get the detailed composition of the requested view
    like fields, model, view architecture

    :param view_id: id of the view or None
    :param view_type: type of the view to return if
    view_id is None ('form', 'tree', ...)
    :param toolbar: true to include contextual actions
    :param submenu: deprecated
    :return: dictionary describing the composition of the
    requested view (including inherited views and extensions)
    :raise AttributeError:
                        * if the inherited view has unknown
                        position to work with other than
                        'before', 'after', 'inside', 'replace'
                        * if some tag other than 'position' is
                        found in parent view
    :raise Invalid ArchitectureError: if there is view type other than
     form, tree, calendar, search etc defined on the structure
    """
    View = self.env['ir.ui.view']

    # Get the view arch and all other attributes describing the composition of
    # the view
    result = self._fields_view_get(
        view_id=view_id,
        view_type=view_type,
        toolbar=toolbar,
        submenu=submenu)

    # Override context for postprocessing
    if view_id and result.get('base_model', self._name) != self._name:
        View = View.with_context(base_model_name=result['base_model'])

    # Apply post processing, groups and modifiers etc...
    xarch, xfields = View.postprocess_and_fields(
        self._name, etree.fromstring(result['arch']), view_id)
    result['arch'] = xarch
    result['fields'] = xfields

    # Add related action information if aksed
    if toolbar:
        bindings = self.env['ir.actions.actions'].get_bindings(self._name)
        resreport = [action
                     for action in bindings['report']
                     if view_type == 'tree' or not action.get('multi')]
        resaction = [action
                     for action in bindings['action']
                     if view_type == 'tree' or not action.get('multi')]
        resrelate = []
        if view_type == 'form':
            resrelate = bindings['action_form_only']

        for res in itertools.chain(resreport, resaction):
            res['string'] = res['name']
        resreport = clear_views_without_print_report(self, view_id, resreport)
        result['toolbar'] = {
            'print': resreport,
            'action': resaction,
            'relate': resrelate,
        }
    return result


def clear_views_without_print_report(self, view_id, resreport):
    views_without_print_report = [
        'project_event.project_event_task_tree',
        'project_event.project_event_task_form',
    ]
    if view_id and self.env['ir.ui.view'].browse(view_id).get_xml_id()[
            view_id] in views_without_print_report:
        resreport = []
    else:
        return resreport


BaseModel.fields_view_get = fields_view_get
