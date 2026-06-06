# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sa_default_area_uom = fields.Selection(
        [('marla', 'Marla'),
         ('kanal', 'Kanal'),
         ('sqft', 'Square Foot'),
         ('sqyd', 'Square Yard'),
         ('sqm', 'Square Meter')],
        string='Default Area Unit', default='marla',
        config_parameter='sa_property_management.default_area_uom')

    sa_property_journal_id = fields.Many2one(
        'account.journal', string='Property Sales Journal',
        domain="[('type', '=', 'sale')]",
        config_parameter='sa_property_management.property_journal_id')

    sa_transfer_journal_id = fields.Many2one(
        'account.journal', string='Property Transfer Journal',
        domain="[('type', 'in', ('sale', 'general'))]",
        config_parameter='sa_property_management.transfer_journal_id')

    sa_default_property_income_account_id = fields.Many2one(
        'account.account', string='Default Property Income Account',
        config_parameter='sa_property_management.default_income_account_id')

    sa_default_dealer_commission = fields.Float(
        string='Default Dealer Commission (%)', digits=(6, 2), default=2.0,
        config_parameter='sa_property_management.default_dealer_commission')

    sa_currency_id = fields.Many2one(
        'res.currency', string='Property Currency (PKR recommended)',
        config_parameter='sa_property_management.currency_id')

    sa_default_payment_term_id = fields.Many2one(
        'account.payment.term', string='Default Payment Terms',
        config_parameter='sa_property_management.default_payment_term_id',
        help="Native Odoo payment terms pre-filled on new bookings and "
             "service assignments, and applied to the invoices they generate.")

    sa_send_payment_reminders = fields.Boolean(
        string='Send Installment Reminders',
        config_parameter='sa_property_management.send_payment_reminders',
        default=True,
        help="When enabled, the system schedules email reminders for due/overdue "
             "installments.")

    sa_doc_footer = fields.Char(
        string='Document Footer Note',
        config_parameter='sa_property_management.doc_footer',
        help="Branded footer line printed on property PDF documents "
             "(receipts, bookings, allocations, customer files).")
    sa_doc_tagline = fields.Char(
        string='Document Tagline',
        config_parameter='sa_property_management.doc_tagline',
        help="Short tagline printed under the company name on documents.")
