# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Move Activity Tasks',
    'version': '11.0.1.0.0',
    'author': 'Savoir-faire Linux, Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Project Management',
    'summary': 'Project Event module',
    'depends': [
        'project_event',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'wizard/project_move_activity_tasks_wizard.xml',
        'views/project_task_view.xml'
    ],
    'installable': True,
    'application': False,
}
