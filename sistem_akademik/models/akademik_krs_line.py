from odoo import models, fields

class AkademikKrsLine(models.Model):
    _name = 'akademik.krs.line'
    _description = 'Study Plan Detail'

    krs_id = fields.Many2one('akademik.krs', string='KRS', ondelete='cascade')
    subject_id = fields.Many2one('akademik.subject', string='Subject', required=True)
    credits = fields.Integer(string='Credits', related='subject_id.credits', readonly=True)
    grade = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E')
    ], string='Grade')
