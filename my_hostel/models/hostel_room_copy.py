from odoo import fields, models, api

class HostelRoomCopy(models.Model):
    _name = "hostel.room.copy"
    _inherit = "hostel.room"
    _description = "Hostel Room Information Copy"
    
    #_inherit = 'hostel.room': "Tolong ambil semua struktur (field & method) dari model Room."
    #_name = 'hostel.room.copy': "Tapi jangan timpa yang lama! Buat tabel database BARU dengan nama ini."