# -*- coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Project Event',
    'version': '11.0.1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Project Management',
    'summary': 'Project Event module',
    'depends': [
        'project',
        'mail',
        'hr',
        'project_resource_calendar'
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/project_security.xml',
        'views/project_project_view.xml',
        'views/project_task_view.xml',
        'views/activity_category_view.xml',
        'views/task_category_view.xml',
        'views/event_template_view.xml',
        'views/activity_template_view.xml',
        'views/task_template_view.xml',
        'data/ir_sequence_data.xml',
    ],
    'installable': True,
    'application': False,
}
