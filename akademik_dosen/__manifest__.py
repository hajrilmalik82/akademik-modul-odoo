{
    'name': 'Dosen Akademik',
    'version': '17.0.1.0.0',
    'description': """Modul Keren Dosen""",
    'author': 'Hajril',
    'depends': ['base', 'hr', 'sistem_akademik'],
    'data': [
        'security/ir.model.access.csv',
        'security/akademik_rules.xml',
        'views/hr_employee_view.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'akademik_dosen/static/src/css/dosen_style.css',
        ],
    },
    'installable': True,
    'application': False,
}
