# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Project Event',
    'version': '11.0.1.0.0',
    'author': 'Savoir-faire Linux, Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Project Management',
    'summary': 'Project Event module',
    'depends': [
        'contacts',
        'project',
        'mail',
        'project_resource_calendar',
        'web_widget_color',
        'web_widget_table',
        'hr_timesheet',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/project_security.xml',
        'data/auditlog_rule.xml',
        'data/channels.xml',
        'data/ir_sequence_data.xml',
        'data/task_categories.xml',
        'report/project_task_activity_report.xml',
        'security/ir.model.access.csv',
        'templates/assets.xml',
        'views/auditlog_log.xml',
        'views/project_project_view.xml',
        'views/project_task_view.xml',
        'views/task_category_view.xml',
        'views/res_partner_view.xml',
        'views/res_partner_category_type_view.xml',
        'views/res_partner_category_view.xml',
        'views/project_task_view.xml',
        'views/res_partner_sector_view.xml',
        'views/hr_department_view.xml',
        'views/calendar_event_view.xml',
        'wizard/reservation_validation_wiz_view.xml'
    ],
    'installable': True,
    'application': False,
}
