from odoo import models, fields, api
from datetime import timedelta

class HostelRoom(models.Model):
    _inherit= 'hostel.room'
    
    date_terminate = fields.Date('Date of Termintaion')
    # 2. OVERRIDE method make_closed
    def make_closed(self):
        # --- LOGIKA TAMBAHAN KITA (SEBELUM) ---
        # Ambil jatah hari dari kategori, kalau kosong default 10 hari
        day_to_allocate = self.category_id.max_allow_days or 10
        
        # Hitung tanggal: Hari ini + Jatah Hari
        termination_date = fields.Date.today() + timedelta(days=day_to_allocate)
        
        # Simpan ke field
        self.date_terminate = termination_date
        
        # --- PANGGIL LOGIKA ASLI (SUPER) ---
        # "Hai Odoo, jalankan fungsi make_closed punya bapaknya (my_hostel)"
        # Ini yang akan mengubah state jadi 'closed'
        return super(HostelRoom, self).make_closed()

    # 3. OVERRIDE method make_available
    def make_available(self):
        # --- LOGIKA TAMBAHAN KITA ---
        # Reset tanggal jadi kosong saat kamar tersedia lagi
        self.date_terminate = False
        
        # --- PANGGIL LOGIKA ASLI ---
        # Ini yang akan mengubah state jadi 'available'
        return super(HostelRoom, self).make_available()