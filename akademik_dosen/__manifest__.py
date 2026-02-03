{
    'name': 'Ekstensi Dosen Akademik',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Manajemen Dosen dan Integrasi Akademik',
    'description': """
        Modul ini memperluas fungsionalitas HR Employee untuk Dosen
        dan menghubungkannya dengan Sistem Akademik.
    """,
    'author': 'Hajril',
    'depends': ['base', 'hr', 'sistem_akademik'],
    'data': [
        'views/hr_employee_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
