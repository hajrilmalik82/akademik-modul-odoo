from odoo import models, _, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for order in self:
            if not order.date_order:
                raise UserError(_("isi Date dahulu."))

            # Informasi Tanggal
            o_date = order.date_order
            o_day = o_date.day
            o_month = o_date.month
            o_year = o_date.year

            deadline_rec = self.env["quota.deadline"].search([], limit=1)
            deadline_day = deadline_rec.deadline_day if deadline_rec else 25

            category_qty_map = {}
            for line in order.order_line:
                if line.display_type: continue 
                
                product_tmpl = line.product_id.product_tmpl_id
                if not product_tmpl.quota_category_id:
                    continue 
                
                qc = product_tmpl.quota_category_id
                category_qty_map.setdefault(qc, 0.0)
                category_qty_map[qc] += line.product_uom_qty

            for qc, requested_qty in category_qty_map.items():
                
                allocation = self.env["quota.allocation"].search([
                    ("quota_category_id", "=", qc.id),
                    ("year", "=", o_year),
                ], limit=1)

                if allocation:
                    # jatah bulan ini
                    alloc_line = allocation.line_ids.filtered(lambda l: l.month == o_month)
                    
                    if alloc_line:
                        global_limit = alloc_line[0].quantity 

                        used_global = self._get_usage(qc.id, o_year, o_month, partner_id=False)

                        if (used_global + requested_qty) > global_limit:
                            raise UserError(_(
                                "GLOBAL QUOTA EXCEEDED (STOP)\n"
                                "Category: %s\n"
                                "Limit Global: %s | Sudah Terpakai: %s\n"
                                "Order Anda: %s menyebabkan over limit."
                            ) % (qc.name, global_limit, used_global, requested_qty))

                if o_day <= deadline_day:
                    
                    # menari Limit Customer
                    customer_quota = self.env["customer.quota"].search([
                        ("partner_id", "=", order.partner_id.id),
                        ("quota_category_id", "=", qc.id),
                        ("year", "=", o_year),
                        ("month", "=", o_month),
                    ], limit=1)

                    if customer_quota:
                        cust_limit = customer_quota.quantity

                        used_cust = self._get_usage(qc.id, o_year, o_month, partner_id=order.partner_id.id)

                        if (used_cust + requested_qty) > cust_limit:
                            raise UserError(_(
                                "CUSTOMER QUOTA EXCEEDED (STOP)\n"
                                "Maaf, Anda melebihi jatah bulanan sebelum tanggal %s.\n"
                                "Customer: %s | Kategori: %s\n"
                                "Limit: %s | Terpakai: %s | Order Ini: %s"
                            ) % (deadline_day, order.partner_id.name, qc.name, cust_limit, used_cust, requested_qty))

        return super().action_confirm()

    def _get_usage(self, category_id, year, month, partner_id=False):
        domain = [
            ('order_id.state', 'in', ['sale', 'done']),
            ('product_id.product_tmpl_id.quota_category_id', '=', category_id),
            ('order_id.id', '!=', self.id)
        ]
        
        if partner_id:
            domain = domain + [('order_id.partner_id', '=', partner_id)]
            
        all_lines = self.env['sale.order.line'].search(domain)
        
        total_used = 0.0
        for line in all_lines:
            d = line.order_id.date_order
            if d and d.year == year and d.month == month:
                total_used += line.product_uom_qty
                    
        return {'type': 'ir.actions.act_window_close'}