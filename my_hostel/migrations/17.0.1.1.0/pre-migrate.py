def migrate(cr, version):
    # Rename kolom 'allocation_date' jadi 'allocation_date_char'
    # Tujuannya: Mengamankan data lama sebelum Odoo membuat kolom baru
    cr.execute('ALTER TABLE hostel_room RENAME COLUMN allocation_date TO allocation_date_char')