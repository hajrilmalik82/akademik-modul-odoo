from odoo import fields
from datetime import date
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    # Ambil ID dan Data Lama (yang sudah direname jadi _char di pre-migrate)
    cr.execute('SELECT id, allocation_date_char FROM hostel_room')
    
    for record_id, old_date in cr.fetchall():
        if not old_date:
            continue
            
        new_date = None
        try:
            # 1. Coba konversi langsung (kalau formatnya YYYY-MM-DD)
            new_date = fields.Date.to_date(old_date)
        except ValueError:
            # 2. Kalau gagal, cek apakah dia cuma nulis TAHUN (misal: "2022")
            if len(old_date) == 4 and old_date.isdigit():
                # Defaultkan ke tanggal 1 Januari tahun tersebut
                new_date = date(int(old_date), 1, 1)
            else:
                _logger.warning(f"Data '{old_date}' pada ID {record_id} tidak bisa dikonversi ke Date. Dikosongkan.")

        # 3. Jika berhasil dikonversi, Update ke kolom baru
        if new_date:
            cr.execute(
                'UPDATE hostel_room SET allocation_date=%s WHERE id=%s',
                (new_date, record_id)
            )