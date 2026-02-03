from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_dosen = fields.Boolean(string='Adalah Dosen', default=False)
    nidn = fields.Char(string='NIDN')
    gelar_akademik = fields.Char(string='Gelar Akademik')
    

