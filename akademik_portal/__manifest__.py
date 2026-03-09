# -*- coding: utf-8 -*-
{
    'name': 'Akademik Student Portal',
    'version': '17.0.1.0.0',
    'summary': 'Student portal — QWeb pages + OWL jadwal filter',
    'category': 'Akademik',
    'license': 'LGPL-3',
    'depends': ['portal', 'sistem_akademik', 'akademik_tesis'],
    'data': [
        'security/portal_security.xml',
        'security/ir.model.access.csv',
        'views/portal_navbar.xml',
        'views/portal_profil.xml',
        'views/portal_krs.xml',
        'views/portal_jadwal.xml',
        'views/portal_tesis.xml',
        'views/portal_menu.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'akademik_portal/static/src/css/portal.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
