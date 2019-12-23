# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

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
