from odoo import models, fields


class AkademikRuangan(models.Model):
    _name = 'akademik.ruangan'
    _description = 'Room'
    
    name = fields.Char(string='Room Name', required=True)
    capacity = fields.Integer(string='Capacity', default=5)
