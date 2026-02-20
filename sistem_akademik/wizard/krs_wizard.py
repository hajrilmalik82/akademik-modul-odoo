from odoo import models, fields, api, _
from odoo.exceptions import UserError

class KrsWizard(models.TransientModel):
    _name = 'akademik.krs.wizard'
    _description = 'KRS Initialization Wizard'

    academic_year_id = fields.Many2one('akademik.tahun', string='Academic Year', required=True)
    entry_year_id = fields.Many2one('akademik.tahun', string='Entry Year (Student Intake)', required=True)
    study_program_id = fields.Many2one('akademik.prodi', string='Study Program', required=True)
    semester = fields.Selection([
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
        ('8', 'Semester 8'),
    ], string='Target Semester', required=True)

    def process_krs(self):
        # 1. Get Candidates
        students = self.env['res.partner'].search([
            ('identitas_mahasiswa', '=', True),
            ('entry_year_id', '=', self.entry_year_id.id),
            ('study_program_id', '=', self.study_program_id.id),
            ('status', '=', 'active')
        ])

        if not students:
            raise UserError(_('No active students found for this Entry Year and Study Program.'))
            
        candidate_count = len(students)

        # 2. Get Subjects based on Semester (Target Semester) AND Study Program
        subjects = self.env['akademik.subject'].search([
            ('study_program_id', '=', self.study_program_id.id),
            ('semester', '=', self.semester)
        ])
        
        if not subjects:
             raise UserError(_(f'No Subjects found for {self.study_program_id.name} Semester {self.semester}. Please configure Subject Semesters first.'))

        # 3. PRE-VALIDATION: Check Capacity vs Candidates
        # Logic: 
        # For each Subject -> Get All Schedules
        # Sum(Room Capacity - Current Enrolled) -> Available Seats
        # If Available Seats < candidate_count -> Error
        
        validation_errors = []
        
        for subject in subjects:
            # Find all schedules for this subject
            # sudo() needed because students might not have access to all schedules
            schedules = self.env['akademik.jadwal'].sudo().search([
                ('subject_id', '=', subject.id)
            ], order='name asc')
            
            if not schedules:
                validation_errors.append(f"- Subject '{subject.name}': No Class Schedules found. Please create at least one class schedule.")
                continue
                
            # Calculate Total Available Seats based on Room Capacity
            # Note: We must check 'remaining_quota' dynamic field
            total_remaining = sum(s.remaining_quota for s in schedules)
            
            if total_remaining < candidate_count:
                details = ", ".join([f"{sch.ruangan_id.name} (Rem: {sch.remaining_quota})" for sch in schedules])
                validation_errors.append(f"- Subject '{subject.name}': Need {candidate_count} seats, but only have {total_remaining} remaining. \n  Current Rooms: [{details}]")
        
        if validation_errors:
            error_msg = "Cannot generate KRS due to insufficient capacity:\n" + "\n".join(validation_errors)
            error_msg += "\n\nPlease add more Class Schedules / Rooms for these subjects."
            raise UserError(_(error_msg))

        # 4. Process Creation (If Validation Passed)
        created_krs = []
        
        for student in students:
            # Check if student already has KRS
            existing_krs = self.env['akademik.krs'].search([
                ('student_id', '=', student.id),
                ('academic_year_id', '=', self.academic_year_id.id),
                ('semester', '=', self.semester)
            ], limit=1)
            
            if existing_krs:
                continue

            krs_vals = {
                'student_id': student.id,
                'academic_year_id': self.academic_year_id.id,
                'semester': self.semester,
                'line_ids': []
            }
            krs_lines = []
            
            for subject in subjects:
                # Auto-Distribution Logic (Sequential Filling)
                # 1. Find all schedules
                # sudo() needed because students might not have access to all schedules
                schedules = self.env['akademik.jadwal'].sudo().search([
                    ('subject_id', '=', subject.id)
                ], order='name asc') 
                
                selected_schedule = False
                
                # 2. Find FIRST schedule with available seats (Sequential)
                for schedule in schedules:
                    # Re-check remaining quota in real-time
                    # We use search_count because 'remaining_quota' is computed
                    current_enrolled = self.env['akademik.krs.line'].search_count([('jadwal_id', '=', schedule.id)])
                    if schedule.ruangan_id and current_enrolled < schedule.ruangan_id.capacity:
                        selected_schedule = schedule
                        break
                
                if selected_schedule:
                    krs_lines.append((0, 0, {
                        'subject_id': subject.id,
                        'jadwal_id': selected_schedule.id
                    }))
                else:
                    # Should not happen if validation passed, unless concurrency issue
                    # Create line without schedule as fallback? Or fail?
                    # Let's create it without schedule so Admin notices
                    krs_lines.append((0, 0, {'subject_id': subject.id}))

            krs_vals['line_ids'] = krs_lines
            
            krs = self.env['akademik.krs'].create(krs_vals)
            created_krs.append(krs.id)

        if not created_krs:
            raise UserError(_('Process Completed. No new KRS records created (Subjects might be missing or students already have KRS).'))
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generated KRS Results',
            'res_model': 'akademik.krs',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', created_krs)],
            'target': 'current',
        }
