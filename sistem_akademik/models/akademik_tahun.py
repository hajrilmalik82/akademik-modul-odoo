from odoo import models, fields

class AkademikTahun(models.Model):
    _name = 'akademik.tahun'
    _description = 'Tahun Akademik'
    _rec_name = 'tahun_akademik'

    tahun_akademik = fields.Char(string='Academic Year', required=True)