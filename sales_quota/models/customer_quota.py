from odoo import models, fields

class CustomerQuota(models.Model):
    _name = "customer.quota"
    _description = "Customer Monthly Quota Limit"
    _rec_name = 'partner_id'

    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    quota_category_id = fields.Many2one("quota.category", string="Category", required=True)
    
    year = fields.Integer(string="Year", required=True, default=2025)
    month = fields.Integer(string="Month", required=True)

    quantity = fields.Float(string="Limit Quantity", required=True, default=0.0)