from odoo import models, fields, api
import datetime

class ResPartner(models.Model):
    _inherit = 'res.partner'

    identitas_mahasiswa = fields.Boolean(string='Student Identity')
    nim = fields.Char(string='NIM')
    prodi_id = fields.Many2one('akademik.prodi', string='Study Program')
    jenjang = fields.Selection([
        ('s1', 'Bachelor'),
        ('pasca', 'Postgraduate')
    ], string='Level')
    level_prestasi = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    ], string='Achievement Level')
    tag_mahasiswa = fields.Many2many(
        'res.partner.category',
        'mahasiswa_tag_rel',
        string='Student Tags'
    )
    tahun_masuk = fields.Many2one('akademik.tahun', string='Entry Year')
    topik_riset = fields.Char(string='Research Topic')
    dosen_pembimbing_id = fields.Many2one('hr.employee', string='Academic Advisor')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('aktif', 'Active'),
        ('lulus', 'Graduated'),
        ('dropout', 'Drop Out')
    ], string='Student Status', default='draft')

    def action_generate_nim(self):
        for record in self:
            if not record.nim:
                year = datetime.datetime.now().year
                record.nim = f"{year}{record.id or '0000'}"
                
    @api.depends('name', 'nim', 'identitas_mahasiswa')
    def _compute_display_name(self):
        super(ResPartner, self)._compute_display_name()
        for record in self:
            if record.nim:
                record.display_name = f"[{record.nim}] {record.name}"
