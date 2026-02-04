{
    'name': 'Dosen Akademik',
    'version': '1.0',
    'description': """Modul Keren Dosen""",
    'author': 'Hajril',
    'depends': ['base', 'hr', 'sistem_akademik'],
    'data': [
        'security/akademik_security.xml',
        'security/ir.model.access.csv',
        'security/akademik_rules.xml',
        'views/hr_employee_view.xml',
        'views/menu_security.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'akademik_dosen/static/src/css/dosen_style.css',
        ],
    },
    'installable': True,
    'application': False,
}
