# © 2019 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class MailActivityMixin(models.AbstractModel):
    _name = 'mail.activity.mixin'
    _inherit = ['mail.activity.mixin']

    activity_user_id = fields.Many2one(
        string="Mail Activity Responsible",
    )
