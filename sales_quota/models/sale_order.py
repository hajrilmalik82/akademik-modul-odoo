from odoo import models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        DEADLINE_DAY = 25
        
        for order in self:
            if not order.date_order:
                raise UserError(_("Isi Date"))
            
            order_date = order.date_order
            order_day = order_date.day
            order_month = order.date_order.month
            order_year = order.date_order.year

            # kumpulkan qty per quota category 
            category_qty = {}

            for line in order.order_line:
                qc = line.product_id.product_tmpl_id.quota_category_id
                if not qc:
                    raise UserError(_(
                        "Product '%s' no Kategori."
                        ) % line.product_id.display_name)

                category_qty.setdefault(qc, 0.0)
                category_qty[qc] += line.product_uom_qty

            for qc, total_qty in category_qty.items():

                allocation = self.env["quota.allocation"].search([
                    ("quota_category_id", "=", qc.id),
                    ("year", "=", order_year),
                ], limit=1)

                if not allocation:
                    raise UserError(_(
                        "No quota allocation found for category '%s' in year %s."
                    ) % (quota_category.name, order_year))  

                alloc_line = allocation.line_ids.filtered(
                    lambda l: l.month == order_month
                )

                if not alloc_line:
                    raise UserError(_(
                        "No quota allocation found for category '%s' in year %s."
                    ) % (quota_category.name, order_year))

                alloc_line = alloc_line[0]

                # BLOCKING
                if total_qty > alloc_line.quantity:
                    raise UserError(_(
                        "Quota exceeded for category %s\n"
                        "Remaining: %s\n"
                        "Requested: %s"
                    ) % (
                        qc.name,
                        alloc_line.quantity,
                        total_qty
                    ))

                # ✅ KURANGI KUOTA
                alloc_line.quantity -= total_qty
                
            if order_day <= DEADLINE_DAY:

                customer_usage = {}

                for line in order.order_line:
                    quota_category = line.product_id.product_tmpl_id.quota_category_id
                    key = (order.partner_id, quota_category)

                    customer_usage.setdefault(key, 0.0)
                    customer_usage[key] += line.product_uom_qty

                for (customer, quota_category), total_qty in customer_usage.items():

                    customer_quota = self.env["customer.quota"].search([
                        ("partner_id", "=", customer.id),
                        ("quota_category_id", "=", quota_category.id),
                        ("year", "=", order_year),
                        ("month", "=", order_month),
                    ], limit=1)

                    if not customer_quota:
                        raise UserError(_(
                            "No customer quota defined.\n\n"
                            "Customer: %s\n"
                            "Category: %s\n"
                            "Period: %s/%s"
                        ) % (
                            customer.name,
                            quota_category.name,
                            order_month,
                            order_year
                        ))

                    if total_qty > customer_quota.quantity:
                        raise UserError(_(
                            "Customer quota exceeded.\n\n"
                            "Customer: %s\n"
                            "Category: %s\n"
                            "Remaining quota: %s\n"
                            "Requested quantity: %s\n\n"
                            "Note: Customer quota is enforced until day %s of the month."
                        ) % (
                            customer.name,
                            quota_category.name,
                            customer_quota.quantity,
                            total_qty,
                            DEADLINE_DAY
                        ))

                    # Kurangi quota customer
                    customer_quota.quantity -= total_qty

        return super().action_confirm()