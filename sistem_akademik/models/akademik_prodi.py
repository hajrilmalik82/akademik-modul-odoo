from odoo import models, fields

class AkademikProdi(models.Model):
    _name = 'akademik.prodi'
    _description = 'Study Program'
    _rec_name = 'study_program_name'
    _order = 'study_program_name'

    _sql_constraints = [
        ('study_program_name_unique', 'unique(study_program_name)', 'Study Program name must be unique!')
    ]

    study_program_name = fields.Char(string='Study Program Name', required=True)
