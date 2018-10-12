# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'mail.thread']

    code = fields.Char(
        string='Number',
    )
    responsible_id = fields.Many2one(
        'res.partner',
        string='Responsible',
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
    )
    project_type = fields.Selection(
        [
            ('event', 'Event'),
            ('project', 'Project'),
        ],
        string='Type',
        default='project',
    )
    notes = fields.Html(string='Notes')
    description = fields.Html(string='Description')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('option', 'Option'),
            ('accepted', 'Accepted'),
            ('canceled', 'Canceled')
        ],
        string='State',
        default='draft',
        track_visibility='onchange',
    )

    @api.multi
    def action_cancel(self):
        self.write({'state': 'canceled'})

    @api.multi
    def action_accept(self):
        self.write({'state': 'accepted'})

    @api.multi
    def action_option(self):
        self.write({'state': 'option'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        if 'project_type' in vals:
            if vals['project_type'] == 'event':
                vals['code'] = self.env['ir.sequence'] \
                    .next_by_code('project.project')
        return super(Project, self).create(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name),
                      ('code', operator, name)]
        return super(Project, self).search(
            domain + args, limit=limit).name_get()
