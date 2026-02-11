from odoo import models, fields, api

class AkademikThesisScore(models.Model):
    _name = 'akademik.tesis.nilai'
    _description = 'Thesis Final Defense Score'
    _rec_name = 'examiner_id'
    _order = 'examiner_id'

    thesis_id = fields.Many2one('akademik.tesis', string='Thesis', required=True, ondelete='cascade')
    examiner_id = fields.Many2one('hr.employee', string='Examiner', required=True, domain="[('is_dosen', '=', True)]")
    score = fields.Integer(string='Score', required=True, default=0)
    note = fields.Text(string='Note')

    @api.constrains('score')
    def _check_score(self):
        for record in self:
            if record.score < 0 or record.score > 100:
                raise models.ValidationError("Score must be between 0 and 100.")
