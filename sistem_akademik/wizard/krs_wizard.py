from odoo import models, fields, api, _
from odoo.exceptions import UserError

class KrsWizard(models.TransientModel):
    _name = 'akademik.krs.wizard'
    _description = 'KRS Initialization Wizard'

    academic_year_id = fields.Many2one('akademik.tahun', string='Academic Year', required=True)
    entry_year_id = fields.Many2one('akademik.tahun', string='Entry Year (Student Intake)', required=True)
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
        students = self.env['res.partner'].search([
            ('identitas_mahasiswa', '=', True),
            ('entry_year_id', '=', self.entry_year_id.id),
            ('status', '=', 'active')
        ])

        if not students:
            raise UserError(_('No active students found for this entry year.'))

        created_krs = []
        
        for student in students:
            if not student.study_program_id:
                continue

            krs_package = self.env['akademik.krs.package'].search([
                ('study_program_id', '=', student.study_program_id.id),
                ('semester', '=', self.semester)
            ], limit=1)

            if not krs_package:
                continue

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
            for subject in krs_package.subject_ids:
                krs_lines.append((0, 0, {'subject_id': subject.id}))
            krs_vals['line_ids'] = krs_lines
            
            krs = self.env['akademik.krs'].create(krs_vals)
            created_krs.append(krs.id)

        if not created_krs:
            raise UserError(_('Process Completed. No new KRS records created (Packages might be missing or students already have KRS).'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generated KRS Results',
            'res_model': 'akademik.krs',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', created_krs)],
            'target': 'current',
        }
