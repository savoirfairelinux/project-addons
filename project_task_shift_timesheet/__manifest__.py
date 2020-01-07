# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Task Shift Timesheet',
    'version': '11.0.1.0.0',
    'author': 'Savoir-faire Linux, Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Project Management',
    'summary': 'Project Event Shift Timesheet module',
    'depends': [
        'project_event',
        'project_resource_calendar'
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'views/project_task_shift_timesheet_view.xml',
        'views/project_task_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
