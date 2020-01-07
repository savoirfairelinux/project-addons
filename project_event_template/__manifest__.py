# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Project Event Template',
    'version': '11.0.1.0.0',
    'author': 'Savoir-faire Linux, Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Project Management',
    'summary': 'Project Event Template Module',
    'depends': [
        'project_event',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/event_template_view.xml',
        'views/activity_template_view.xml',
        'views/task_template_view.xml',
        'wizard/project_event_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
}
