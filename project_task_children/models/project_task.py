# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class Task(models.Model):
    _inherit = ['project.task']


    child_ids = fields.One2many('project.task', string="Sub-tasks", context={'active_test': True})
