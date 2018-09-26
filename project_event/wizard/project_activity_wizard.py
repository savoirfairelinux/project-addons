# @ 2018 Savoir-failre Linux
# License LGPL-3.0 or Later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProjectActivityWizard(models.TransientModel):
    """Wizard Event Activity Creation from template"""
    _name = 'project.activity.wizard'
    _description = __doc__

    event_wizard_id = fields.Many2one(
        'project.event.wizard',
        string='Event Wizard',
    )
    template_id = fields.Many2one(
        'activity.template',
        string='Activity Template',
    )
    name = fields.Char(
        string='Activity Title',
    )
    activity_resp_id = fields.Many2one(
        'res.partner',
        string='Responsible',
    )
    activity_category_id = fields.Many2one(
        'activity.category',
        string='Category',
    )
    room_id = fields.Many2one(
        'resource.resource',
        string='Room',
    )
    notes = fields.Text(
        string='Notes',
    )
