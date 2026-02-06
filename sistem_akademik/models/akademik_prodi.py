from odoo import models, fields

class AkademikProdi(models.Model):
    _name = 'akademik.prodi'
    _description = 'Program Studi'
    _rec_name = 'nama_prodi'

    nama_prodi = fields.Char(string='Study Program Name', required=True)
