# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Calendar Event Report',
    'version': '11.0.1.0.0',
    'author': 'Savoir-faire Linux, Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Calendar',
    'summary': 'Calendar Event Report module',
    'depends': [
        'calendar',
        'project_resource_calendar',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'report/calendar_event_report.xml',
        'report/calendar_event_print_template.xml',
        'wizard/weekly_report_wizard.xml',
        'wizard/weekly_report_template.xml',
    ],
    'installable': True,
    'application': False,
}
