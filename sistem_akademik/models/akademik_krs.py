from odoo import models, fields

class AkademikKrs(models.Model):
    _name = 'akademik.krs'
    _description = 'Student Study Plan'
    _rec_name = 'student_id'
    _order = 'academic_year_id desc, semester desc'

    active = fields.Boolean(default=True)
    
    student_id = fields.Many2one('res.partner', string='Student', domain="[('identitas_mahasiswa', '=', True)]", required=True)
    study_program_id = fields.Many2one('akademik.prodi', string='Study Program', related='student_id.study_program_id', store=True, readonly=True)
    academic_year_id = fields.Many2one('akademik.tahun', string='Academic Year', required=True)
    semester = fields.Selection([
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
        ('8', 'Semester 8')
    ], string='Semester', required=True)
    line_ids = fields.One2many('akademik.krs.line', 'krs_id', string='Study Plan Details')
