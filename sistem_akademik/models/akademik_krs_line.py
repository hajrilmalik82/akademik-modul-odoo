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
    jadwal_id = fields.Many2one('akademik.jadwal', string='Class Schedule')

    @api.onchange('jadwal_id')
    def _onchange_jadwal_id(self):
        if self.jadwal_id:
            self.subject_id = self.jadwal_id.subject_id

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
