from odoo import models, fields, api


class AkademikKrsLine(models.Model):
    _name = 'akademik.krs.line'
    _description = 'Study Plan Detail'

    krs_id = fields.Many2one('akademik.krs', string='KRS', ondelete='cascade')
    subject_id = fields.Many2one('akademik.subject', string='Subject', required=True)
    credits = fields.Integer(string='Credits', related='subject_id.credits', readonly=True)
    jadwal_id = fields.Many2one('akademik.jadwal', string='Class Schedule')

    # ── Komponen Nilai ────────────────────────────────────────────
    score_harian = fields.Float(string='Nilai Harian (30%)', default=0, digits=(5, 2))
    score_uts = fields.Float(string='Nilai UTS (30%)', default=0, digits=(5, 2))
    score_uas = fields.Float(string='Nilai UAS (40%)', default=0, digits=(5, 2))

    # ── Total & Grade (computed) ──────────────────────────────────
    score = fields.Float(
        string='Total Score', compute='_compute_score', store=True, readonly=True, digits=(5, 2))
    grade = fields.Selection([
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')
    ], string='Grade', compute='_compute_grade', store=True, readonly=True)

    is_thesis = fields.Boolean(compute='_compute_is_thesis', string='Is Thesis')

    # ── Access helper (untuk lock field di view) ──────────────────
    dosen_access_ok = fields.Boolean(
        string='Can Edit Score', compute='_compute_dosen_access_ok')

    @api.depends('score_harian', 'score_uts', 'score_uas')
    def _compute_score(self):
        for record in self:
            record.score = (
                record.score_harian * 0.30 +
                record.score_uts    * 0.30 +
                record.score_uas    * 0.40
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

    @api.depends('jadwal_id')
    def _compute_dosen_access_ok(self):
        """True jika user adalah dosen pengajar jadwal ini, atau officer."""
        user = self.env.user
        is_officer = user.has_group('sistem_akademik.group_akademik_officer')
        for record in self:
            if is_officer:
                record.dosen_access_ok = True
            elif record.jadwal_id and record.jadwal_id.dosen_id:
                record.dosen_access_ok = (
                    record.jadwal_id.dosen_id.user_id.id == user.id)
            else:
                record.dosen_access_ok = False

    @api.onchange('jadwal_id')
    def _onchange_jadwal_id(self):
        if self.jadwal_id:
            self.subject_id = self.jadwal_id.subject_id

    @api.depends('subject_id')
    def _compute_is_thesis(self):
        for record in self:
            if record.subject_id and record.subject_id.name:
                record.is_thesis = 'tesis' in record.subject_id.name.lower()
            else:
                record.is_thesis = False

    @api.constrains('score_harian', 'score_uts', 'score_uas')
    def _check_score_range(self):
        for record in self:
            for field_name, val in [
                ('Nilai Harian', record.score_harian),
                ('Nilai UTS', record.score_uts),
                ('Nilai UAS', record.score_uas),
            ]:
                if not (0 <= val <= 100):
                    raise models.ValidationError(
                        f"{field_name} harus antara 0 dan 100 (nilai: {val})")

    @api.constrains('jadwal_id')
    def _check_schedule_conflict(self):
        for record in self:
            if not record.jadwal_id:
                continue
            
            # Check Conflict
            # Check for conflict with other lines in the SAME KRS (or other active KRS of the same student)
            # Find other KRS lines of this student that have a schedule
            domain = [
                ('krs_id.student_id', '=', record.krs_id.student_id.id),
                ('id', '!=', record.id),
                ('jadwal_id', '!=', False),
                ('krs_id.active', '=', True)
            ]
            other_lines = self.sudo().search(domain)
            
            for line in other_lines:
                # Check Day Collision
                # Use sudo() to access jadwal details as they might be hidden
                sch_a = record.jadwal_id.sudo()
                sch_b = line.jadwal_id.sudo()
                
                if sch_b.day == sch_a.day:
                    # Check Time Overlap
                    # (StartA < EndB) and (EndA > StartB)
                    if (sch_a.start_time < sch_b.end_time) and (sch_a.end_time > sch_b.start_time):
                        raise models.ValidationError(
                            f"Schedule Conflict! Class '{sch_a.name}' overlaps with '{sch_b.name}' on {sch_a.day} at {sch_a.start_time}-{sch_a.end_time}."
                        )
            
            # Check Quota (Capacity)
            # Count how many lines use this jadwal_id
            # sudo() ESSENTIAL here because student cannot see other students' lines
            current_enrolled = self.sudo().search_count([('jadwal_id', '=', record.jadwal_id.id)])
            
            # Use Room Capacity as limit
            sch_sudo = record.jadwal_id.sudo()
            limit = sch_sudo.ruangan_id.capacity if sch_sudo.ruangan_id else 0
            
            if current_enrolled > limit:
                raise models.ValidationError(f"Class '{sch_sudo.name}' is Full! Capacity: {limit}")

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
