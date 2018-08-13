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
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'views/project_project_view.xml',
        'views/project_event_type_view.xml',
        'data/ir_sequence_data.xml',
    ],
    'installable': True,
    'application': False,
}
