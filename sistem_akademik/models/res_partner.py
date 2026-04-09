from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [
        ('nim_unique', 'unique(nim)', 'NIM must be unique!')
    ]

    is_student = fields.Boolean(string='Student Identity')
    nim = fields.Char(string='NIM')
    study_program_id = fields.Many2one('akademik.prodi', string='Study Program')
    achievement_level = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    ], string='Achievement Level')
    student_tags = fields.Many2many(
        'res.partner.category',
        'mahasiswa_tag_rel',
        string='Student Tags'
    )
    entry_year_id = fields.Many2one('akademik.tahun', string='Entry Year')
    research_topic = fields.Char(string='Research Topic')
    supervisor_id = fields.Many2one('hr.employee', string='Academic Advisor')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('dropout', 'Drop Out')
    ], string='Student Status', default='draft')

    def action_generate_nim(self):
        for record in self:
            if not record.nim:
                # Use ir.sequence for robust NIM generation
                record.nim = self.env['ir.sequence'].next_by_code('res.partner.nim') or 'New'
                
    @api.depends('name', 'nim', 'is_student')
    def _compute_display_name(self):
        super(ResPartner, self)._compute_display_name()
        for record in self:
            # sudo() bypasses hr.employee.public proxy restriction when this
            # partner is also linked to an employee account
            nim = record.sudo().nim
            if nim:
                record.display_name = f"[{nim}] {record.name}"

    @api.model
    def _name_search(self, name='', domain=None, operator='ilike', limit=100, order=None):
        """Allow searching partners by NIM in Many2one dropdowns."""
        domain = domain or []
        if name:
            domain = ['|', ('nim', operator, name), ('name', operator, name)] + domain
        return super()._name_search(name='', domain=domain, operator=operator, limit=limit, order=order)

    def action_open_my_profile(self):
        """Opens the logged-in student's own profile in form view."""
        partner = self.env.user.partner_id
        form_view = self.env.ref('sistem_akademik.view_partner_form_mahasiswa')
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Profile',
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
            'views': [(form_view.id, 'form')],
            'target': 'current',
            'flags': {'mode': 'readonly'},
        }

    def action_generate_portal_user(self):
        """Generate a Portal User account for this student.
        Portal users access the system via /my/ and cannot enter the Odoo backend."""
        if not self.env.user.has_group('sistem_akademik.group_akademik_officer'):
            raise models.ValidationError(
                _("Only Academic Officers can generate student user accounts."))

        for record in self:
            if not record.is_student:
                continue

            if record.user_ids:
                raise models.ValidationError(
                    _(f"Student '{record.name}' already has a user account."))

            if not record.email:
                raise models.ValidationError(
                    _(f"Please fill in the email for '{record.name}' first."))

            # Mencegah database integrity collision crash (Clean Code: Anggun menangkap Error)
            existing_user = self.env['res.users'].sudo().search([('login', '=', record.email)])
            if existing_user:
                raise models.ValidationError(_(f"Email '{record.email}' is already registered to another user."))

            user_vals = {
                'name': record.name,
                'login': record.email,
                'email': record.email,
                # Portal user only — NO base.group_user (internal)
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
            }
            user = self.env['res.users'].sudo().create(user_vals)
            record.sudo().write({'user_ids': [(4, user.id)]})

