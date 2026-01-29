{
    'name': "Hostel Termination",
    'summary': "Manage room termination dates",
    'description': "Menambahkan logika hitung tanggal otomatis saat kamar ditutup.",
    'author': "Hajril",
    'website': "http://www.example.com",
    'category': 'Uncategorized',
    'version': '17.0.1.0.0',
    # WAJIB: Modul ini butuh my_hostel supaya bisa jalan
    'depends': ['base', 'my_hostel'], 
    'data': [
        'views/hostel_room.xml',
    ],
}