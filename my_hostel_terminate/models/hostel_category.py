from odoo import models, fields

class HostelRoomCategory(models.Model):
    _inherit = 'hostel.category' # mewarisi model yang sudah ada
    
    #menambahkan field baru ke model lama
    max_allow_days = fields.Integer(
        string="Maximum Days",
        help="Berapa lama kamar boleh dipinjam (hari)",
        default=365
    )