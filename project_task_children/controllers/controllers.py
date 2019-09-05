# -*- coding: utf-8 -*-
from odoo import http

# class ProjectTaskChildren(http.Controller):
#     @http.route('/project_task_children/project_task_children/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_task_children/project_task_children/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_task_children.listing', {
#             'root': '/project_task_children/project_task_children',
#             'objects': http.request.env['project_task_children.project_task_children'].search([]),
#         })

#     @http.route('/project_task_children/project_task_children/objects/<model("project_task_children.project_task_children"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_task_children.object', {
#             'object': obj
#         })