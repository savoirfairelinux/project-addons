# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Project Resource Calendar',
    'version': '1.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Project',
    'summary': 'Project Resource Calendar',
    'depends': [
        'auditlog',
        'calendar_resource',
        'resource',
        'calendar',
        'hr',
        'web_timeline',
    ],
    'external_dependencies': {
        'python': [],
    },
    'qweb': [
        'templates/calendar_template.xml',
    ],
    'data': [
        'data/auditlog_rule.xml',
        'security/calendar_security.xml',
        'security/ir.model.access.csv',
        'views/auditlog_log.xml',
        'views/calendar_event_view.xml',
        'views/resource_view.xml',
        'views/room_view.xml',
        'views/instrument_view.xml',
        'templates/assets.xml',
        'report/calendar_event_report.xml',
        'report/calendar_event_print_template.xml',
        'wizard/weekly_report_wizard.xml',
        'wizard/weekly_report_template.xml',
        'views/room_type_view.xml',
        'views/miscellaneous_view.xml',
    ],
    'installable': True,
    'application': True,
}
