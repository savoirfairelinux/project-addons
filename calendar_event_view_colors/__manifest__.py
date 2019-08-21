# © 2019 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Calendar Event View Colors',
    'version': '11.0.1.0.0',
    'author': 'Savoir-faire Linux, Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Calendar',
    'summary': 'Calendar Event View Color',
    'depends': [
        'base',
        'project',
        'calendar',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'views/calendar_event_view.xml',
        'views/project_task_view.xml',
        'views/task_category_view.xml',
        'views/calendar_color_tag_fields_view.xml',
        'templates/assets.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
