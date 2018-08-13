# coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProjectEventType(models.Model):
    _name = 'project.event.type'

    name = fields.Char(
        string='Name',
    )
