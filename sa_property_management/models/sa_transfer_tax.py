# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaTransferTax(models.Model):
    """Configurable tax applied on a property transfer.

    Covers Pakistani taxes such as CVT, Stamp Duty, Registration Fee,
    Capital Gains Tax (CGT) and FBR withholding under Sec. 236C/236K.
    """
    _name = 'sa.transfer.tax'
    _description = 'Property Transfer Tax'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, help="Short code, e.g. CVT, STAMP, REG.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)

    computation = fields.Selection(
        [('fixed', 'Fixed Amount'),
         ('percent', 'Percentage of Sale Price'),
         ('percent_dc', 'Percentage of DC Value')],
        default='percent', required=True,
        help="DC Value = Deputy Commissioner notified value used by FBR for tax "
             "computation. Falls back to sale price when DC value is not set.")
    rate = fields.Float(
        string='Rate (%)', digits=(6, 4),
        help="Percentage rate. Used when computation is percentage based.")
    fixed_amount = fields.Monetary(
        currency_field='currency_id',
        help="Fixed amount. Used when computation is 'Fixed Amount'.")
    currency_id = fields.Many2one(
        related='company_id.currency_id', store=True, readonly=True)

    payer = fields.Selection(
        [('buyer', 'Buyer'),
         ('seller', 'Seller'),
         ('shared', 'Shared (50/50)')],
        default='buyer', required=True)

    account_id = fields.Many2one(
        'account.account',
        domain="[('company_ids', 'in', company_id)]",
        help="Account credited when this tax is posted with the transfer entry.")

    property_type_filter = fields.Selection(
        [('all', 'All Types'),
         ('plot', 'Plot only'),
         ('house', 'House only'),
         ('apartment', 'Apartment only'),
         ('commercial', 'Commercial only')],
        default='all', required=True,
        help="Restrict where this tax is auto-applied.")

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)',
         'Tax code must be unique per company.'),
    ]

    @api.constrains('rate', 'fixed_amount', 'computation')
    def _check_amounts(self):
        for rec in self:
            if rec.computation in ('percent', 'percent_dc') and rec.rate <= 0:
                raise ValidationError(_("Tax '%s' uses a percentage but the rate is zero.", rec.name))
            if rec.computation == 'fixed' and rec.fixed_amount <= 0:
                raise ValidationError(_("Tax '%s' uses a fixed amount but the amount is zero.", rec.name))

    def compute_tax(self, sale_price, dc_value=False):
        """Return the tax amount for a given sale price and optional DC value."""
        self.ensure_one()
        base = sale_price or 0.0
        if self.computation == 'fixed':
            return self.fixed_amount
        if self.computation == 'percent_dc':
            base = dc_value or sale_price or 0.0
        return base * (self.rate or 0.0) / 100.0
