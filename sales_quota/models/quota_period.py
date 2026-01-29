from odoo import models, fields, api, _

class QuotaPeriod(models.Model):
    _name = "quota.period"
    _description = "quota priod"
    _order = "year desc, month desc"
    _rec_name = "display_name"

    year = fields.Integer(required=True, default=2025)
    month = fields.Integer(required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Processed')
    ], string="Status", default='draft', readonly=True)
    
    processed_at = fields.Datetime("Processed Date", readonly=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)

    _sql_constraints = [
        ('unique_period', 'unique(year, month)', 'Periode bulan ini sudah dibuat!')
    ]

    @api.depends('year', 'month')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.year} - Bulan {rec.month}"