# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    _order = 'sequence, name'

    sequence = fields.Integer(
        string='Sequence',
    )
