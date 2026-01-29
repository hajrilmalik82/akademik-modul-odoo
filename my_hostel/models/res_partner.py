from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    # Field 1: Penanda apakah dia Rektor Asrama
    is_hostel_rector = fields.Boolean("Hostel Rector", 
        help="Activate if the following person is hostel rector")
    
    # Field 2: Hubungan ke Room (Koreksi  menjadi hostel.room)
    # Kita pakai Many2many agar satu orang bisa pegang banyak room, 
    # dan satu room (mungkin) bisa dipegang banyak orang.
    assign_room_ids = fields.Many2many(
        'hostel.room',             # Target Model (Kamar)
        string='Assigned Rooms',
        help="Rooms assigned to this rector"
    )
    
    # Field 3: Menghitung jumlah kamar (Computed Field)
    count_assign_room = fields.Integer(
        string='Number of Assigned Rooms', 
        compute="_compute_count_room"
    )

    @api.depends('assign_room_ids')
    def _compute_count_room(self):
        for partner in self:
            # Fungsi len() menghitung jumlah data di dalam list assign_room_ids
            partner.count_assign_room = len(partner.assign_room_ids)