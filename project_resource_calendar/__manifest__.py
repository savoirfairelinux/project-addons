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
        'views/room_type.xml',
        'views/equipment_calendar.xml',
        'views/resource.xml',
        'views/sector.xml',
        'views/room.xml',
        'views/instrument.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
