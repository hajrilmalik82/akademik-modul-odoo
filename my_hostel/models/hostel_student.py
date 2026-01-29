from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.tests.common import Form

class HostelStudent(models.Model):
    _name = "hostel.student"
    _description = "Hostel Student Information"
    
    # --- BAGIAN BARU: DELEGATION INHERITANCE ---
    # Artinya: Model ini 'nebeng' ke model res.partner
    _inherits = {'res.partner': 'partner_id'}
    
    # Field Penghubung (Link) ke Partner
    # ondelete='cascade' artinya: kalau Partner dihapus, Student ini juga ikut terhapus otomatis
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    # -------------------------------------------

    # --- PERHATIAN: Field 'name' yang lama DIHAPUS/KOMENTAR ---
    # Kenapa? Karena sekarang kita pakai 'name' milik res.partner
    # name = fields.Char("Student Name")  <-- INI WAJIB DIKOMENTAR/HAPUS
    
    # Field spesifik milik Student (Bukan milik Partner)
    gender = fields.Selection([("male", "Male"),
        ("female", "Female"), ("other", "Other")],
        string="Gender", help="Student gender")
        
    active = fields.Boolean("Active", default=True,
        help="Activate/Deactivate hostel record")
    
    room_id = fields.Many2one("hostel.room", "Room",
        help="Select hostel room")
        
    hostel_id = fields.Many2one("hostel.hostel", related='room_id.hostel_id',
        string="Hostel", store=True, readonly=True)
    
    status = fields.Selection([("draft", "Draft"),
        ("reservation", "Reservation"), ("pending", "Pending"),
        ("paid", "Done"),("discharge", "Discharge"), ("cancel", "Cancel")],
        string="Status", copy=False, default="draft",
        help="State of the student hostel")
    
    admission_date = fields.Date("Admission Date",
        help="Date of admission in hostel",
        default=fields.Datetime.today)
    discharge_date = fields.Date("Discharge Date", help="Date on which student discharge")
    
    duration = fields.Integer("Duration", compute="_compute_check_duration", inverse="_inverse_duration",
        help="Enter duration of living")
    
    duration_onchange = fields.Integer("Duration On Change", inverse="_inverse_duration",
        help="Enter duration of living")
    
    # ... (Method compute dan inverse tetap sama, tidak berubah) ...
    @api.depends("admission_date", "discharge_date")
    def _compute_check_duration(self):
        for rec in self:
            if rec.discharge_date and rec.admission_date:
                rec.duration = (rec.discharge_date - rec.admission_date).days
            else:
                rec.duration = 0

    def _inverse_duration(self):
        for stu in self:
            if stu.admission_date and stu.duration:
                stu.discharge_date = stu.admission_date + timedelta(days=stu.duration)
                
    def action_assign_room(self):
        self.ensure_one()
        # 1. Cek pembayaran
        if self.status != "paid":
            raise UserError(_("You can't assign a room if it's not paid.")) 

        # 3. Panggil model Room dengan SUDO (Mode Dewa)
        room_as_superuser = self.env['hostel.room'].sudo()
        
        # 4. Create Kamar
        room_rec = room_as_superuser.create({
            "name": "Room for-" + self.name,
            "room_no": "RM-" + str(self.id),
            "floor_no": 1,
            #"category_id": self.env.ref("my_hostel.single_room_categ").id, 
            "hostel_id": self.hostel_id.id,
            "student_per_room": 3,
        })
        
        # 5. Sambungkan ke siswa
        self.sudo().room_id = room_rec.id
        
    def action_assign_room_wizards(self):
         return {
            'type': 'ir.actions.act_window',
            'name': _('Assign Room'),
            'res_model': 'assign.room.student.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
        }
        
    def action_remove_room(self):
        if self.env.context.get("is_hostel_room"):
            self.room_id = False
    
    # 1. Dekorator: Menentukan field mana yang jadi "Pemicu"
    @api.onchange('admission_date', 'discharge_date')
    def onchange_duration(self):
        # 2. Cek apakah kedua tanggal sudah diisi?
        # Kalau salah satu kosong, jangan hitung (nanti error)
        if self.discharge_date and self.admission_date:
            
            # 3. Logika Matematika (Menghitung selisih Bulan)
            # (Selisih Tahun * 12) + Selisih Bulan
            year_diff = self.discharge_date.year - self.admission_date.year
            month_diff = self.discharge_date.month - self.admission_date.month
            
            self.duration_onchange = (year_diff * 12) + month_diff
    
    def return_room(self):
        self.ensure_one()
        
        # 1. Siapkan Model Wizard
        wizard_model = self.env['assign.room.student.wizard']
        
        # 2. Buka "Form Virtual"
        # with Form(...) as form: -> Ini seperti membuka popup di layar
        with Form(wizard_model) as return_form:
            
            # 3. Isi Data (Pemicu Onchange)
            # Saat baris ini jalan, seolah-olah user memilih kamar.
            # Jika di wizard ada onchange untuk 'room_id', dia AKAN JALAN di sini.
            return_form.room_id = self.env['hostel.room'].search([], limit=1)
         
        # 4. Simpan Form (Klik Save)
        # Ini akan menghasilkan record wizard asli di database
        wizard_record = return_form.save()
        
        # 5. Jalankan Aksi Wizard
        # Panggil fungsi logic wizardnya, jangan lupa bawa context
        wizard_record.with_context(active_id=self.id).add_room_in_student()