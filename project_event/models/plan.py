# © 2019 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Plan(models.Model):
    _name = 'project.event.plan'

    name = fields.Char(
        string='Title',
    )
    plan = fields.Binary(
        "Plan",
        help="Add Plan",
        attachment=True,
    )
