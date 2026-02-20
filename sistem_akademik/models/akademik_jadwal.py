from odoo import models, fields, api

class AkademikJadwal(models.Model):
    _name = 'akademik.jadwal'
    _description = 'Class Session'
    
    name = fields.Char(string='Class Name', compute='_compute_name', store=True)
    subject_id = fields.Many2one('akademik.subject', string='Subject', required=True)
    study_program_id = fields.Many2one('akademik.prodi', string='Study Program')
    semester = fields.Selection(related='subject_id.semester', string='Semester', store=True, readonly=True)
    
    @api.onchange('study_program_id')
    def _onchange_study_program_id(self):
        if self.study_program_id:
            return {'domain': {'subject_id': [('study_program_id', '=', self.study_program_id.id)]}}
        else:
            return {'domain': {'subject_id': []}}

    @api.onchange('subject_id')
    def _onchange_subject_id(self):
        if self.subject_id and self.subject_id.study_program_id:
            self.study_program_id = self.subject_id.study_program_id.id
    
    day = fields.Selection([
        ('senin', 'Monday'),
        ('selasa', 'Tuesday'),
        ('rabu', 'Wednesday'),
        ('kamis', 'Thursday'),
        ('jumat', 'Friday'),
        ('sabtu', 'Saturday'),
        ('minggu', 'Sunday')
    ], string='Day', required=True)
    
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)
    
    ruangan_id = fields.Many2one('akademik.ruangan', string='Room', required=True)
    dosen_id = fields.Many2one('hr.employee', string='Lecturer', domain="[('is_dosen', '=', True)]")
    
    # One2many to KRS Line to count enrolled students and for domain filtering
    line_ids = fields.One2many('akademik.krs.line', 'jadwal_id', string='KRS Lines')
    
    enrolled_count = fields.Integer(string='Enrolled', compute='_compute_enrolled')
    remaining_quota = fields.Integer(string='Remaining Quota', compute='_compute_enrolled')
    
    @api.depends('subject_id', 'day', 'start_time', 'ruangan_id')
    def _compute_name(self):
        for record in self:
            if record.subject_id and record.day and record.ruangan_id:
                record.name = f"{record.subject_id.name} ({record.ruangan_id.name}) - {record.day.capitalize()} {record.start_time}"
            else:
                record.name = "New Class"

    def _compute_enrolled(self):
        for record in self:
            # sudo() needed to count ALL students, not just what user can see
            record.enrolled_count = self.env['akademik.krs.line'].sudo().search_count([('jadwal_id', '=', record.id)])
            if record.ruangan_id:
                record.remaining_quota = record.ruangan_id.capacity - record.enrolled_count
            else:
                record.remaining_quota = 0

    def action_claim_schedule(self):
        self.ensure_one()
        # Find Employee linked to current User
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        
        if not employee:
            raise models.ValidationError("Your user is not linked to any Employee/Lecturer data.")
            
        if not employee.is_dosen:
             raise models.ValidationError("You are not registered as a Lecturer.")
             
        # Check Prodi Match
        if self.study_program_id and employee.study_program_id:
            if self.study_program_id != employee.study_program_id:
                raise models.ValidationError(f"You cannot claim schedule from other Study Program ({self.study_program_id.name}). Your Homebase is {employee.study_program_id.name}.")

        if self.dosen_id:
            raise models.ValidationError(f"This schedule is already taken by {self.dosen_id.name}.")
            
        self.dosen_id = employee.id
        return True

    def action_release_schedule(self):
        self.ensure_one()
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        
        if not employee or not employee.is_dosen:
             raise models.ValidationError("You are not authorized.")
             
        if self.dosen_id != employee:
            raise models.ValidationError("You cannot release a schedule that is not yours.")
            
        self.dosen_id = False
        return True
