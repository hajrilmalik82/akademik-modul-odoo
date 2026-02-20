from odoo import models, fields

class AkademikSubject(models.Model):
    _name = 'akademik.subject'
    _description = 'Academic Subject'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    credits = fields.Integer(string='Credits', required=True)
    type = fields.Selection([
        ('compulsory', 'Compulsory'),
        ('elective', 'Elective')
    ], string='Type', required=True, default='compulsory')
    
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

    study_program_id = fields.Many2one('akademik.prodi', string='Study Program', required=True)
