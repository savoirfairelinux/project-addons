# © 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Resource Calendar',
    'version': '11.0.1.0.0',
    'author': 'Savoir-faire Linux, Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Project',
    'summary': 'Project Resource Calendar',
    'depends': [
        'auditlog',
        'resource_calendar',
        'resource',
        'calendar',
        'hr',
        'web_timeline',
        'web',
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
        'views/service_view.xml',
        'views/res_partner_view.xml',
        'views/res_groups.xml',
        'views/hr_employee_view.xml',
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
    'images': [
        'static/description/conflict_prompt.png',
        'static/description/piano_on_stage.png',
        'static/description/room_screenshot.png',
        'static/description/main_screenshot.png'
    ]
}
