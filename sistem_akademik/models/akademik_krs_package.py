from odoo import models, fields

class AkademikKrsPackage(models.Model):
    _name = 'akademik.krs.package'
    _description = 'KRS Package'
    _order = 'study_program_id, semester'

    name = fields.Char(string='Package Name', required=True)
    study_program_id = fields.Many2one('akademik.prodi', string='Study Program', required=True)
    semester = fields.Selection([
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
        ('8', 'Semester 8'),
    ], string='Semester', required=True)
    subject_ids = fields.Many2many('akademik.subject', string='Subjects')
