{
    'name': 'Akademik Tesis',
    'version': '17.0.1.0.0',
    'author': 'Hajril',
    'depends': ['base', 'sistem_akademik', 'akademik_dosen'],
    'data': [
        'security/ir.model.access.csv',
        'security/akademik_rule.xml',
        'views/tesis_view.xml',
        'views/dashboard_view.xml',
        'views/menu.xml',
        'report/surat_lulus_tesis.xml',
    ],
    'installable': True,
    'application': True,
}
