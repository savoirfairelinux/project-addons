# © 2019 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Resources reservation from project tasks",
    'summary': """
        This module enable users to reserve resources from project tasks""",
    'description': """
        This module enable users to reserve resources from project tasks
    """,
    'author': 'Savoir-faire Linux, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-auth',
    'license': 'AGPL-3',
    'category': 'Tools',
    'version': '11.0.1.0.0',
    'depends': ['project',
                'calendar_resource'],
    'data': [
        'views/project_task_view.xml',
    ],
}