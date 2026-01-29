from odoo import models, fields, api, _
from odoo.exceptions import UserError

class QuotaBatchWizard(models.TransientModel):
    _name = 'quota.batch.wizard'
    _description = 'Batch Processing Wizard'

    def _default_period(self):
        if self.env.context.get('active_model') == 'quota.period':
            return self.env.context.get('active_id')
        return False

    period_id = fields.Many2one(
        "quota.period", 
        string="Period to Process", 
        required=True,
        default=_default_period,
        readonly=True
    )
    
    year = fields.Integer(related="period_id.year", readonly=True)
    month = fields.Integer(related="period_id.month", readonly=True)

    def action_process(self):
        self.ensure_one()
        period = self.period_id

        prev_month = self.month - 1
        prev_year = self.year
        if prev_month == 0:
            prev_month = 12
            prev_year = self.year - 1

        prev_period = self.env['quota.period'].search([
            ('year', '=', prev_year),
            ('month', '=', prev_month)
        ], limit=1)

        if prev_period and prev_period.state != 'done':
            raise UserError(_("Bulan lalu belum selesai."))

        self.env['quota.over.limit'].search([('period_id', '=', period.id)]).unlink()

        orders = self.env['sale.order'].search([
            ('state', 'in', ['sale', 'done']),
            ('date_order', '>=', f'{self.year}-{self.month:02d}-01'),
            ('date_order', '<=', f'{self.year}-{self.month:02d}-31'),
        ])
        
        usage_map = {} 
        for order in orders:
            for line in order.order_line:
                if line.display_type or not line.product_id.product_tmpl_id.quota_category_id:
                    continue
                key = (order.partner_id.id, line.product_id.product_tmpl_id.quota_category_id.id)
                usage_map.setdefault(key, 0.0)
                usage_map[key] += line.product_uom_qty

        vals_list = []
        for (partner_id, category_id), total_used in usage_map.items():
            cust_quota = self.env['customer.quota'].search([
                ('partner_id', '=', partner_id),
                ('quota_category_id', '=', category_id),
                ('year', '=', self.year),
                ('month', '=', self.month)
            ], limit=1)
            limit = cust_quota.quantity if cust_quota else 0.0

            if total_used > limit:
                self.env['quota.over.limit'].create({
                    'period_id': period.id,
                    'partner_id': partner_id,
                    'quota_category_id': category_id,
                    'year': self.year,
                    'month': self.month,
                    'limit_qty': limit,
                    'used_qty': total_used,
                    'over_qty': total_used - limit
                })

        period.write({'state': 'done', 'processed_at': fields.Datetime.now()})
        
        return {'type': 'ir.actions.act_window_close'}