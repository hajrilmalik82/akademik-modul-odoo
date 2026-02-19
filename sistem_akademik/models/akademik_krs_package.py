from odoo import models, fields, api

class AkademikKrsPackage(models.Model):
    _name = 'akademik.krs.package'
    _description = 'KRS Package'
    _order = 'study_program_id, semester'

    name = fields.Char(string='Package Name', required=True)
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
    ], string='Semester', required=True)
    subject_ids = fields.Many2many('akademik.subject', string='Subjects', domain="[('study_program_id', '=', study_program_id)]")

    @api.constrains('subject_ids')
    def _check_unique_subjects(self):
        for package in self:
            # Check if any subject in this package is already used in OTHER packages
            other_packages = self.search([('id', '!=', package.id)])
            existing_subject_ids = other_packages.mapped('subject_ids').ids
            
            for subject in package.subject_ids:
                if subject.id in existing_subject_ids:
                    raise models.ValidationError(f"Subject '{subject.name}' is already used in another package! A subject can only be assigned to one package.")
