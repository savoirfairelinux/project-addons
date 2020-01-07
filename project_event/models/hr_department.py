# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    _order = 'sequence, name'

    sequence = fields.Integer(
        string='Sequence',
    )
