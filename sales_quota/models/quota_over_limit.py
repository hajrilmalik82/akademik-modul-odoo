from odoo import models, fields

class QuotaOverLimit(models.Model):
    _name = "quota.over.limit"
    _description = "quota limi"
    _order = "year desc, month desc, over_qty desc"

    period_id = fields.Many2one("quota.period", string="Period", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Customer", readonly=True)
    quota_category_id = fields.Many2one("quota.category", string="Category", readonly=True)
    
    year = fields.Integer(readonly=True)
    month = fields.Integer(readonly=True)
    
    limit_qty = fields.Float(string="Limit", readonly=True)
    used_qty = fields.Float(string="Total Used", readonly=True)
    over_qty = fields.Float(string="Over Amount", readonly=True)