from odoo import models, fields, api

class AkademikKrsScoreWizard(models.TransientModel):
    _name = 'akademik.krs.score.wizard'
    _description = 'Wizard Input Score'

    krs_line_id = fields.Many2one('akademik.krs.line', string='Study Plan Detail', required=True, readonly=True)
    score = fields.Integer(string='Score (0-100)', required=True)

    @api.model
    def default_get(self, fields):
        res = super(AkademikKrsScoreWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            line = self.env['akademik.krs.line'].browse(active_id)
            res.update({
                'krs_line_id': line.id,
                'score': line.score,
            })
        return res

    def action_save_score(self):
        self.ensure_one()
        self.krs_line_id.score = self.score
        return {'type': 'ir.actions.act_window_close'}
