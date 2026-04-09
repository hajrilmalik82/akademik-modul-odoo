from odoo import models, fields, api, _


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

    room_id = fields.Many2one('akademik.ruangan', string='Room', required=True)
    lecturer_id = fields.Many2one('hr.employee', string='Lecturer', domain="[('is_lecturer', '=', True)]")

    # One2many to KRS Line to count enrolled students and for domain filtering
    line_ids = fields.One2many('akademik.krs.line', 'schedule_id', string='KRS Lines')

    enrolled_count = fields.Integer(string='Enrolled', compute='_compute_enrolled')
    remaining_quota = fields.Integer(string='Remaining Quota', compute='_compute_enrolled')

    @api.depends('subject_id', 'day', 'start_time', 'room_id')
    def _compute_name(self):
        for record in self:
            if record.subject_id and record.day and record.room_id:
                record.name = f"{record.subject_id.name} ({record.room_id.name}) - {record.day.capitalize()} {record.start_time}"
            else:
                record.name = "New Class"

    @api.depends('line_ids', 'room_id')
    def _compute_enrolled(self):
        for record in self:
            # sudo() needed to count ALL students, not just what user can see
            record.enrolled_count = self.env['akademik.krs.line'].sudo().search_count([('schedule_id', '=', record.id)])
            if record.room_id:
                record.remaining_quota = record.room_id.capacity - record.enrolled_count
            else:
                record.remaining_quota = 0

    def action_claim_schedule(self):
        self.ensure_one()
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

        if not employee:
            raise models.ValidationError(_("Your user is not linked to any Employee/Lecturer data."))

        if not employee.is_lecturer:
            raise models.ValidationError(_("Only users with the Lecturer role can claim schedules."))

        # Check Prodi Match
        if self.study_program_id and employee.study_program_id:
            if self.study_program_id != employee.study_program_id:
                raise models.ValidationError(_(f"You cannot claim schedule from other Study Program ({self.study_program_id.name}). Your Homebase is {employee.study_program_id.name}."))

        if self.lecturer_id:
            raise models.ValidationError(_(f"This schedule is already taken by {self.lecturer_id.name}."))

        self.lecturer_id = employee.id
        return True

    def action_release_schedule(self):
        self.ensure_one()
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

        if not employee or not employee.is_lecturer:
            raise models.ValidationError(_("You must be logged in as the related Lecturer to release this schedule."))

        if self.lecturer_id != employee:
            raise models.ValidationError(_("You cannot release a schedule that is not yours."))

        self.lecturer_id = False
        return True
