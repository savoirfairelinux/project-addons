# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Task(models.Model):
    _inherit = ['project.task']
    _rec_name = 'complete_name'

    color = fields.Char(
        related='category_id.color'
    )
    font_color = fields.Selection([
        ('black', 'Black (Default)'),
        ('white', 'White')],
        related='category_id.font_color'
    )
    task_state = fields.Selection([
        ('draft', 'Draft'),
        ('option', 'Option'),
        ('requested', 'Requested'),
        ('read', 'Read'),
        ('accepted', 'Accepted'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('postponed', 'Postponed'),
        ('canceled', 'Canceled')],
        string='State',
        default='draft',
        track_visibility='onchange',
    )
    category_id = fields.Many2one(
        'task.category',
        string='Category',
        default=lambda self: self.env['task.category'].search(
            [('is_default', '=', True)]),
        track_visibility='onchange',
    )
