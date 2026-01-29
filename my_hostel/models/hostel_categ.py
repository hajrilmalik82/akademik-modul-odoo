from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HostelCategory(models.Model):
    _name = "hostel.category"
    _description = "Hostel Category"
    _parent_store = True  # Mengaktifkan dukungan hirarki cepat
    _parent_name = "parent_id" # Nama field yang merujuk ke induk

    name = fields.Char('Category', required=True)
    description = fields.Text('Description')
    
    # Field m2o merujuk ke model yang sama (self-reference)
    parent_id = fields.Many2one(
        'hostel.category',
        string='Parent Category',
        ondelete='restrict', # Mencegah hapus induk jika ada anak
        index=True)
    
    # Field wajib untuk menyimpan jalur hirarki
    parent_path = fields.Char(index=True, unaccent=False)
    
    # Field o2m untuk melihat semua sub-kategori di bawahnya
    child_ids = fields.One2many(
        'hostel.category', 'parent_id',
        string='Child Categories')

    # Validasi untuk mencegah hubungan berulang (looping)
    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise ValidationError('Error! You cannot create recursive categories.')