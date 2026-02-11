from odoo import models, fields

class AkademikTahun(models.Model):
    _name = 'akademik.tahun'
    _description = 'Academic Year'
    _rec_name = 'academic_year'
    _order = 'academic_year desc'

    academic_year = fields.Char(string='Academic Year', required=True)