from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [
        ('nim_unique', 'unique(nim)', 'NIM must be unique!')
    ]

    identitas_mahasiswa = fields.Boolean(string='Student Identity')
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
                
    @api.depends('name', 'nim', 'identitas_mahasiswa')
    def _compute_display_name(self):
        super(ResPartner, self)._compute_display_name()
        for record in self:
            if record.nim:
                record.display_name = f"[{record.nim}] {record.name}"
