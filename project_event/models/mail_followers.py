# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class Followers(models.Model):
    _name = 'mail.followers'
    _inherit = ['mail.followers']

    @api.model
    def create(self, vals):
        if vals['res_model'] == 'project.task' and 'partner_id' in vals:
            uniq_follower = self.env['mail.followers'].search(
                [
                    ('res_id', '=', int(vals['res_id'])),
                    ('partner_id', '=', int(vals['partner_id'])),
                    ('res_model', '=', vals['res_model'])
                ]
            )
            if uniq_follower:
                return uniq_follower[0]

        res = super(Followers, self).create(vals)
        res._invalidate_documents()
        return res
