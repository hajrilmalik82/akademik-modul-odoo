from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_dosen = fields.Boolean(string='Is Lecturer', default=False)
    nidn = fields.Char(string='NIDN')
    gelar_akademik = fields.Char(string='Academic Degree')
    
    def action_generate_user(self):
        for employee in self:
            if employee.user_id:
                continue
            
            if not employee.work_email:
                raise models.ValidationError('fill in the email')
                
            user_vals = {
                'name': employee.name,
                'login': employee.work_email,
                'email': employee.work_email,
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
            }
            user = self.env['res.users'].sudo().create(user_vals)
            employee.user_id = user.id
    

