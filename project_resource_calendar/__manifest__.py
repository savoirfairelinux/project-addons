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
        'calendar_resource',
        'resource',
        'calendar',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/room_type_view.xml',
        'views/equipment_calendar_view.xml',
        'views/resource_view.xml',
        'views/sector_view.xml',
        'views/room_view.xml',
        'views/instrument_view.xml',
    ],
    'installable': True,
    'application': True,
}
