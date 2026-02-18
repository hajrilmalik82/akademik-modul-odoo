from odoo import models, fields, api

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
    ], string='Grade', compute='_compute_grade', store=True, readonly=True)
    score = fields.Integer(string='Score (0-100)', default=0)
    
    is_thesis = fields.Boolean(compute='_compute_is_thesis', string='Is Thesis')

    @api.depends('subject_id')
    def _compute_is_thesis(self):
        for record in self:
            if record.subject_id and record.subject_id.name:
                record.is_thesis = 'tesis' in record.subject_id.name.lower()
            else:
                record.is_thesis = False

    @api.depends('score')
    def _compute_grade(self):
        for record in self:
            if record.score >= 85:
                record.grade = 'A'
            elif record.score >= 70:
                record.grade = 'B'
            elif record.score >= 55:
                record.grade = 'C'
            elif record.score >= 40:
                record.grade = 'D'
                record.grade = 'E'

    def action_open_score_wizard(self):
        return {
            'name': 'Input Score',
            'type': 'ir.actions.act_window',
            'res_model': 'akademik.krs.score.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_krs_line_id': self.id, 'default_score': self.score},
        }
