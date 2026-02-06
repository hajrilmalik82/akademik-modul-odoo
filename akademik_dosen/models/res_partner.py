from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    dosen_pembimbing_id = fields.Many2one('hr.employee', string='Supervisor')
