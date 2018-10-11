# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResourceGroupAccess(models.Model):
    """Group Access Rights for Resources"""
    _name = "resource.group.access"
    _description = __doc__

    resource_id = fields.Many2one(
        'resource.calendar.room',
        string='Resource',
    )
    has_access_create = fields.Boolean(
        'Create',
    )
    has_access_write = fields.Boolean(
        'Write',
    )
    has_access_read = fields.Boolean(
        'Read',
    )
    has_access_delete = fields.Boolean(
        'Delete',
    )
    group_id = fields.Many2one(
        string='Group',
        comodel_name='res.groups',
    )
