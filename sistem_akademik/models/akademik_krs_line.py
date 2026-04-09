from odoo import models, fields, api, _


class AkademikKrsLine(models.Model):
    _name = 'akademik.krs.line'
    _description = 'Study Plan Detail'

    krs_id = fields.Many2one('akademik.krs', string='KRS', ondelete='cascade')
    subject_id = fields.Many2one('akademik.subject', string='Subject', required=True)
    credits = fields.Integer(string='Credits', related='subject_id.credits', readonly=True)
    schedule_id = fields.Many2one('akademik.jadwal', string='Class Schedule')

    # ── Komponen Nilai (untuk MK biasa) ─────────────────────────
    daily_score = fields.Float(string='Daily Score (30%)', default=0, digits=(5, 2))
    midterm_score = fields.Float(string='Mid-Term Score (30%)', default=0, digits=(5, 2))
    final_exam_score = fields.Float(string='Final Exam Score (40%)', default=0, digits=(5, 2))

    # ── Nilai khusus Tesis (dari modul akademik_tesis) ────────────
    thesis_score = fields.Float(
        string='Thesis Score', default=0, digits=(5, 2),
        help='Automatically filled from thesis final defense score. For Thesis subject only.')

    # ── Total & Grade (computed) ──────────────────────────────────
    score = fields.Float(
        string='Total Score', compute='_compute_score', store=True, readonly=True, digits=(5, 2))
    grade = fields.Selection([
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')
    ], string='Grade', compute='_compute_grade', store=True, readonly=True)

    is_thesis = fields.Boolean(compute='_compute_is_thesis', string='Is Thesis')

    # ── Access helper (untuk lock field di view) ──────────────────
    is_lecturer_access = fields.Boolean(
        string='Can Edit Score', compute='_compute_is_lecturer_access')

    @api.depends('daily_score', 'midterm_score', 'final_exam_score', 'thesis_score', 'is_thesis')
    def _compute_score(self):
        for record in self:
            if record.is_thesis:
                # Tesis: nilai langsung dari sidang, bukan dari 3 komponen
                record.score = record.thesis_score
            else:
                # MK biasa: bobot harian 30% + UTS 30% + UAS 40%
                record.score = (
                    record.daily_score * 0.30 +
                    record.midterm_score    * 0.30 +
                    record.final_exam_score    * 0.40
                )

    @api.depends('score')
    def _compute_grade(self):
        for record in self:
            s = record.score
            if s >= 85:
                record.grade = 'A'
            elif s >= 70:
                record.grade = 'B'
            elif s >= 55:
                record.grade = 'C'
            elif s >= 40:
                record.grade = 'D'
            else:
                record.grade = 'E'

    @api.depends('schedule_id')
    def _compute_is_lecturer_access(self):
        """True jika user adalah dosen pengajar jadwal ini, atau officer."""
        user = self.env.user
        is_officer = user.has_group('sistem_akademik.group_akademik_officer')
        for record in self:
            if is_officer:
                record.is_lecturer_access = True
            elif record.schedule_id and record.schedule_id.lecturer_id:
                record.is_lecturer_access = (
                    record.schedule_id.lecturer_id.user_id.id == user.id)
            else:
                record.is_lecturer_access = False

    @api.onchange('schedule_id')
    def _onchange_schedule_id(self):
        if self.schedule_id:
            self.subject_id = self.schedule_id.subject_id

    @api.depends('subject_id')
    def _compute_is_thesis(self):
        for record in self:
            if record.subject_id and record.subject_id.name:
                record.is_thesis = 'tesis' in record.subject_id.name.lower()
            else:
                record.is_thesis = False

    @api.constrains('daily_score', 'midterm_score', 'final_exam_score')
    def _check_score_range(self):
        for record in self:
            for field_name, val in [
                ('Nilai Harian', record.daily_score),
                ('Nilai UTS', record.midterm_score),
                ('Nilai UAS', record.final_exam_score),
            ]:
                if not (0 <= val <= 100):
                    raise models.ValidationError(
                        _(f"{field_name} must be between 0 and 100 (value: {val})"))

    @api.constrains('schedule_id')
    def _check_schedule_conflict(self):
        for record in self:
            if not record.schedule_id:
                continue

            domain = [
                ('krs_id.student_id', '=', record.krs_id.student_id.id),
                ('id', '!=', record.id),
                ('schedule_id', '!=', False),
                ('krs_id.active', '=', True)
            ]
            other_lines = self.sudo().search(domain)

            for line in other_lines:
                # sudo() needed: student cannot see other students' jadwal directly
                sch_a = record.schedule_id.sudo()
                sch_b = line.schedule_id.sudo()

                if sch_b.day == sch_a.day:
                    # Time overlap: (StartA < EndB) and (EndA > StartB)
                    if (sch_a.start_time < sch_b.end_time) and (sch_a.end_time > sch_b.start_time):
                        raise models.ValidationError(
                            _(f"Schedule Conflict! Class '{sch_a.name}' overlaps with '{sch_b.name}' on {sch_a.day} at {sch_a.start_time}-{sch_a.end_time}.")
                        )

            # sudo() needed: student cannot see other students' KRS lines
            current_enrolled = self.sudo().search_count([('schedule_id', '=', record.schedule_id.id)])
            sch_sudo = record.schedule_id.sudo()
            limit = sch_sudo.room_id.capacity if sch_sudo.room_id else 0

            if current_enrolled > limit:
                raise models.ValidationError(_(f"Class '{sch_sudo.name}' is Full! Capacity: {limit}"))

    def action_open_score_wizard(self):
        self.ensure_one()
        return {
            'name': 'Input Nilai',
            'type': 'ir.actions.act_window',
            'res_model': 'akademik.krs.score.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_krs_line_id': self.id,
                'default_daily_score': self.daily_score,
                'default_midterm_score': self.midterm_score,
                'default_final_exam_score': self.final_exam_score,
            },
        }
