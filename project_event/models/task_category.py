# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class TaskCategory(models.Model):
    """Event Task Category"""
    _name = 'task.category'
    _description = __doc__
    _order = 'sequence, name, id'

    name = fields.Char(
        string='Name',
        translate=True,
    )
    sequence = fields.Integer(
        string='Sequence',
    )
    color = fields.Char()
    is_default = fields.Boolean(
        string='Default',
    )
    font_color = fields.Selection([
        ('black', 'Black (Default)'),
        ('white', 'White')],
        default='black')

    @api.constrains('is_default')
    def _change_is_default(self):
        if self.is_default:
            task_categories = self.env['task.category'].search(
                [('id', '!=', self.id)])
            for task_category in task_categories:
                task_category.is_default = False

    @api.multi
    def unlink(self):
        for record in self:
            if record.is_default:
                raise ValidationError(
                    _(
                        'The default category cannot be \
                            deleted: \n Default category: '
                        + record.name,
                    )
                )
        return super(TaskCategory, self).unlink()

    @api.model
    def get_category_list(self):
        return list(map(lambda category: {"id": category.id,
                                          "name": category.name,
                                          "color": category.color,
                                          "font_color": category.font_color,
                                          },
                        self.env['task.category'].search([])))
