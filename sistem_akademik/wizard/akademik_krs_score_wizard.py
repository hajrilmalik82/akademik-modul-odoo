from odoo import models, fields, api


class AkademikKrsScoreWizard(models.TransientModel):
    _name = 'akademik.krs.score.wizard'
    _description = 'Wizard Input Score'

    krs_line_id = fields.Many2one(
        'akademik.krs.line', string='Study Plan Detail', required=True, readonly=True)

    score_harian = fields.Float(string='Nilai Harian (30%)', digits=(5, 2), default=0)
    score_uts    = fields.Float(string='Nilai UTS (30%)',    digits=(5, 2), default=0)
    score_uas    = fields.Float(string='Nilai UAS (40%)',    digits=(5, 2), default=0)

    # Preview total
    score_preview = fields.Float(
        string='Total (Preview)', compute='_compute_preview', digits=(5, 2))
    grade_preview = fields.Char(
        string='Grade (Preview)', compute='_compute_preview')

    @api.depends('score_harian', 'score_uts', 'score_uas')
    def _compute_preview(self):
        for rec in self:
            total = rec.score_harian * 0.3 + rec.score_uts * 0.3 + rec.score_uas * 0.4
            rec.score_preview = total
            if total >= 85:
                rec.grade_preview = 'A'
            elif total >= 70:
                rec.grade_preview = 'B'
            elif total >= 55:
                rec.grade_preview = 'C'
            elif total >= 40:
                rec.grade_preview = 'D'
            else:
                rec.grade_preview = 'E'

    def action_save_score(self):
        self.ensure_one()
        # Akses dikontrol oleh ir.rule pada model akademik.krs.line:
        # - Dosen: hanya bisa write baris yang jadwalnya dia yang mengajar
        # - Officer: bisa write semua
        # Jika dosen bukan pengajar jadwal ini, write akan di-reject otomatis oleh rule
        self.krs_line_id.write({
            'score_harian': self.score_harian,
            'score_uts':    self.score_uts,
            'score_uas':    self.score_uas,
        })
        return {'type': 'ir.actions.act_window_close'}
