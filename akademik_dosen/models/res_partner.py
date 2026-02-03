from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Model Refactoring: Changing relation from res.partner to hr.employee
    dosen_pembimbing_id = fields.Many2one(
        'hr.employee', 
        string='Dosen Pembimbing',
        domain="[('is_dosen', '=', True)]" # Filter only Dosen
    )
