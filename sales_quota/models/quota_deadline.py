from odoo import models, fields, api
from odoo.exceptions import ValidationError

class QuotaDeadline(models.Model):
    _name = "quota.deadline"
    _description = "Monthly Quota Deadline Configuration"

    name = fields.Char(default="Monthly Configuration")
    deadline_day = fields.Integer(string="Deadline", required=True, default=25)

    @api.constrains('deadline_day')
    def _check_day(self):
        for rec in self:
            if rec.deadline_day < 1 or rec.deadline_day > 31:
                raise ValidationError("Tanggal Deadline harus antara 1 sampai 31.")