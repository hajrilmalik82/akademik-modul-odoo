import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError # Import untuk Error
from odoo.tools.translate import _    # Import untuk Terjemahan

_logger = logging.getLogger(__name__)

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default=True)
    
    def do_archive(self):
        for record in self:
            record.active = not record.active

class HostelRoom(models.Model):
    
    _name = "hostel.room"
    _description = "Hostel Room Information"
    _rec_name = "room_no"
    
    @api.depends("student_per_room", "student_ids")
    def _compute_check_availability(self):
        """Method to check room availability"""
        for rec in self:
            rec.availability = rec.student_per_room - len(rec.student_ids.ids)
            
    category_id = fields.Many2one("hostel.category", string="Category")
    name = fields.Char(string="Room Name", required=True)
    room_no = fields.Char("Room No.", required=True)
    floor_no = fields.Integer("Floor No", default=1, help="Floor Number")
    currency_id = fields.Many2one('res.currency', string='currency')
    rent_amount = fields.Monetary('Rent Amount', help="Enter rent amount per mount")
    # optional attribute: currency_field='currency_id' incase currency field have another name then 'currency_id'
    hostel_id = fields.Many2one("hostel.hostel", "hostel",help="Name of hostel")
    hostel_amenities_ids = fields.Many2many("hostel.amenities",
        "hostel_room_amenities_rel", "room_id", "amenitiy_id",
        string="Amenities", domain="[('active', '=', True)]",
        help="Select hostel room amenities")
    student_ids = fields.One2many("hostel.student", "room_id", string="Students", help="Enter students")
    student_per_room = fields.Integer("Student Per Room", required=True, help="Students allocated per room")
    availability = fields.Float(compute="_compute_check_availability",
        store=True, string="availability", help="Room availability in hostel")
    state = fields.Selection([
        ('draft', 'Unavailable'),
        ('available', 'Available'),
        ('closed', 'Closed')],
        'State', default="draft")
    room_rating = fields.Float('Rating', default=0.0)
    remaks = fields.Text(string='Remaks')
    # Field Dummy untuk mengetes pencarian
    previous_room_id = fields.Many2one('hostel.room', string='Previous Room')
    allocation_date = fields.Date('Allocation Date')
    
    _sql_constraints = [
        ("Room_no_unique", "unique(room_no)", "Room number must be unique!")]
    
    # 2. Override CREATE (Saat bikin baru)
    @api.model
    def create(self, values):
        # Cek: Apakah user mau ngisi field 'remarks'?
        if values.get('remarks'):
            # Cek: Apakah user INI bukan Manager?
            if not self.user_has_groups('my_hostel.group_hostel_manager'):
                # Kalau bukan manager, tolak!
                raise UserError('Eits! Anda bukan Manager. Dilarang isi Remarks.')
        # Kalau lolos (atau gak ngisi remarks), jalankan create asli
        return super(HostelRoom, self).create(values)
    
    # 3. Override WRITE (Saat edit data lama)
    def write(self, values):
        # Cek: Apakah user mau ngubah field 'remarks'?
        if values.get('remarks'):
            # Cek: Apakah user INI bukan Manager?
            if not self.user_has_groups('my_hostel.group_hostel_manager'):
                raise UserError('Eits! Anda bukan Manager. Dilarang ubah Remarks.')
        # Kalau lolos, jalankan write asli
        return super(HostelRoom, self).write(values)
    
    
    @api.constrains("rent_amount")
    def _cek_rent_amount(self):
        """Contraint on negative rent amount"""
        if self.rent_amount < 0:
            raise ValidationError(_("Rent Amount Per Month should not be a negative value!"))
        
     # Helper Method: Mengecek apakah perpindahan status diizinkan   
    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [
            ('draft','available'),
            ('available', 'closed'),
            ('closed', 'draft')
        ]
        return (old_state, new_state) in allowed
    # 3. Method Utama: Mengubah status kamar
    def change_state(self, new_state):
        for room in self:
            if room.is_allowed_transition(room.state, new_state):
                room.state = new_state
            else:
                # Siapkan pesan error
                # Gunakan _() agar teks bisa diterjemahkan ke bahasa lain nantinya
                msg = _('Moving from %s to %s is not allowed') % (room.state, new_state)
                # Tampilkan Pop-up Error ke layar user
                raise UserError(msg)
            
    # 4. Method Wrapper: Fungsi yang akan dipanggil oleh Tombol
    def make_available(self):
        self.change_state('available') 
    def make_closed(self):
        self.change_state('closed')
    def make_draft(self):
        self.change_state('draft')
        
    def log_all_room_members(self):
        hostel_room_obj = self.env['hostel.room.member']  # This is an empty recordset of model hostel.room.member
        all_members = hostel_room_obj.search([])
        print("ALL MEMBERS:", all_members)
        return True
    
    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }
        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }
        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        # Total 3 records (1 parent and 2 child) will be created in hostel.category model
        record = self.env['hostel.category'].create(parent_category_val)
        return True
    
    
    def update_room_no(self):
        # 1. Pastikan cuma 1 record yang diproses
        self.ensure_one()
        # 2. Update Nilai Field secara Langsung (Option 1)
        self.room_no = "RM002"
        
    def find_room(self):
        domain = [
            '|',
                '&', ('name', 'ilike', 'Room'),
                     ('room_no', '=', 'rm'),
                '&', ('name', 'ilike', 'Second Room Name'),
                     ('room_no', '=', 'Second Category Name')
        ]
        Rooms = self.search(domain)
        _logger.info('Room found: %s', Rooms)
        return True
    
    def test_recordset_operations(self):
        # Skenario: Kita ambil 2 kelompok data berbeda
        
        # Kelompok A: Semua kamar yang statusnya 'Draft'
        rs_draft = self.search([('state', '=', 'draft')]) # [cite: 469-470]
        
        # Kelompok B: Semua kamar yang statusnya 'Available'
        rs_available = self.search([('state', '=', 'available')])
        
        # Kelompok C: Semua kamar (Draft + Available + Closed)
        rs_all = self.search([])

        print("=== MULAI TEST RECORDSET ===")
        print("Draft:", rs_draft)
        print("Available:", rs_available)

        # 1. UNION (|) - Gabungan Tanpa Duplikat
        # Menggabungkan Draft dan Available menjadi satu list unik.
        result_union = rs_draft | rs_available # [cite: 475]
        print("1. UNION (|):", result_union)

        # 2. ADDITION (+) - Penjumlahan (Concatenation)
        # Menggabungkan dua list dengan mempertahankan urutan.
        # Draft ditaruh di depan, Available ditaruh di belakangnya.
        result_add = rs_draft + rs_available # [cite: 473]
        print("2. ADD (+):", result_add)

        # 3. INTERSECTION (&) - Irisan (Data yang Sama)
        # Mencari data yang ada di "Semua Kamar" TAPI JUGA ada di "Available".
        # Logikanya: Hasilnya pasti sama dengan rs_available.
        result_intersect = rs_all & rs_available # [cite: 476]
        print("3. INTERSECTION (&):", result_intersect)
        
        # 4. DIFFERENCE (-) - Selisih
        # Dari "Semua Kamar", buang yang "Available".
        # Sisanya harusnya tinggal Draft dan Closed.
        result_diff = rs_all - rs_available
        print("4. DIFFERENCE (-):", result_diff)
        
        print("=== SELESAI ===")
        return True
    
    def filter_members(self):
        all_rooms = self.search([])
        filtered_rooms = self.rooms_with_multiple_members(all_rooms)
        _logger.info('Filtered Rooms: %s', filtered_rooms)

    @api.model
    def rooms_with_multiple_members(self, all_rooms):
        def predicate(room):
            if len(room.student_ids) > 1:
                return True
        return all_rooms.filtered(predicate)
    
    @api.model
    def get_members_names(self, rooms):
        # MAPPED: Masuk ke field 'member_ids', lalu ambil field 'name'
        # Hasilnya adalah List Python (bukan Recordset) berisi string nama.
        return rooms.mapped('student_ids.name') #

    # --- FUNGSI TOMBOL (Untuk Ngetes) ---
    def test_mapped(self):
        # 1. Ambil semua kamar
        all_rooms = self.search([])
        
        # 2. Panggil fungsi mapped tadi
        names = self.get_members_names(all_rooms)
        
        # 3. Cetak Hasil
        print("=== HASIL MAPPED ===")
        print("Input (Rooms):", all_rooms)
        print("Output (Member Names):", names)
        
        return True
    
    @api.model
    def sort_rooms_by_rating(self, rooms):
        # sorted() bekerja di Memory Python.
        # key='room_rating' artinya urutkan berdasarkan field tersebut.
        # reverse=True artinya dari BESAR ke KECIL (5.0 ke 0.0)
        return rooms.sorted(key='room_rating', reverse=True) #

    # --- FUNGSI TEST (Untuk Tombol) ---
    def test_sorting(self):
        all_rooms = self.search([]) # Ambil semua kamar (urutan default ID)
        
        # Panggil fungsi sorting
        sorted_rooms = self.sort_rooms_by_rating(all_rooms)
        
        print("=== HASIL SORTING (RATING TERTINGGI) ===")
        for room in sorted_rooms:
            print(f"Kamar: {room.name} | Rating: {room.room_rating}")
            
        return True
    
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        
        # Jika user mengetik sesuatu (name tidak kosong)
        if name:
            # Kita manipulasi domain pencariannya
            # Menggunakan operator '|' (OR)
            # Cari di Name ATAU Room No ATAU Nama Siswa
            domain = ['|', '|',
                      ('name', operator, name),
                      ('room_no', operator, name),
                      ('student_ids.name', operator, name)
                     ] + domain
            
            # Reset name jadi kosong saat panggil super, 
            # karena kita sudah memasukkan logika pencarian ke dalam variable 'domain'
            name = ''
            
        return super(HostelRoom, self)._name_search(
            name, domain, operator, limit, order
        )
        
    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(
            # 1. Filter: Cari yang rent_amount-nya tidak kosong
            domain=[('rent_amount', "!=", False)], 
            
            # 2. Fields: Ambil Kategori & Rata-rata Rent Amount
            # Perhatikan sintaks ':avg' di belakang nama field
            fields=['category_id', 'rent_amount:avg'], 
            
            # 3. Group By: Kelompokkan per Kategori
            groupby=['category_id'] 
        )
        return grouped_result

    def test_read_group(self):
        hasil = self._get_average_cost()
        
        print("\n========== HASIL RATA-RATA HARGA SEWA ==========")
        for data in hasil:
            # Ambil Nama Kategori (cegah error jika kategori kosong)
            kategori = data['category_id'][1] if data['category_id'] else 'Tanpa Kategori'
            
            # Ambil nilai rata-rata dari key 'rent_amount'
            rata_rata = data['rent_amount'] 
            
            print(f"Kategori: {kategori} | Rata-Rata Sewa: Rp {rata_rata:,.2f}")
        print("================================================\n")
        return True
    
    @api.model
    def update_price_by_category(self, category_id, amount):
        # Cari kamar yang kategorinya sesuai parameter
        rooms = self.search([('category_id', '=', category_id)])
        for room in rooms:
            room.rent_amount += amount
            
    def action_remove_room_members(self):
        for student in self.student_ids:
            student.with_context(is_hostel_room=True).action_remove_room()
            
    def action_category_with_amount(self):
        self.env.cr.execute("""
            SELECT
                hrc.name,
                hostel_room.rent_amount
            FROM
                hostel_room AS hostel_room
            JOIN
                hostel_category as hrc ON hrc.id = hostel_room.category_id
            WHERE hostel_room.category_id = %(cate_id)s;""", 
            {'cate_id': self.category_id.id})
        result = self.env.cr.fetchall()
        _logger.warning("Hostel Room With Amount: %s", result)
