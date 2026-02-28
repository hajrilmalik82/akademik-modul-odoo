from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_dosen = fields.Boolean(string='Is Lecturer', default=False)
    nidn = fields.Char(string='NIDN')
    study_program_id = fields.Many2one('akademik.prodi', string='Study Program (Homebase)')

    def action_generate_user(self):
        for employee in self:
            if employee.user_id:
                continue

            if not employee.work_email:
                raise models.ValidationError("Please fill in the work email for the employee.")

            # Ensure the current user is an HR Manager or Academic Officer
            if not self.env.user.has_group('sistem_akademik.group_akademik_officer'):
                raise models.AccessError("You are not allowed to generate users. Please contact HR Manager.")

            user_vals = {
                'name': employee.name,
                'login': employee.work_email,
                'email': employee.work_email,
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('sistem_akademik.group_akademik_dosen').id])]
            }
            # Use sudo to allow creation of user/partner bypassing strict record rules
            user = self.env['res.users'].sudo().create(user_vals)
            employee.sudo().user_id = user.id


class HrEmployeePublic(models.Model):
    """Wajib ada di Odoo 17: expose field custom agar non-HR user
    (mahasiswa/dosen) bisa baca data employee melalui proxy hr.employee.public.
    Tanpa ini, membaca jadwal_id.dosen_id di KRS form akan Access Error."""
    _inherit = 'hr.employee.public'

    is_dosen = fields.Boolean(readonly=True)
    nidn = fields.Char(readonly=True)
    study_program_id = fields.Many2one('akademik.prodi', readonly=True)
