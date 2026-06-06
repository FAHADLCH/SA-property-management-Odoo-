# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaPropertyBooking(models.Model):
    """Booking / Sale agreement between a customer and a property.

    Lifecycle:
        draft  ───▶  confirmed  ───▶  in_payment  ───▶  completed
                                                 │
                                                 └─▶  cancelled
    """
    _name = 'sa.property.booking'
    _description = 'Property Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sa.qr.mixin']
    _order = 'booking_date desc, id desc'

    _sa_doc_type = _('Property Booking')

    name = fields.Char(string='Booking Reference', required=True, copy=False,
                       default=lambda self: _('New'), tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('in_payment', 'In Payment'),
         ('completed', 'Completed'),
         ('cancelled', 'Cancelled')],
        default='draft', required=True, tracking=True, copy=False)

    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.company.currency_id,
        help="Transaction currency. Defaults from the property/project and "
             "flows to the generated customer invoices.")

    customer_id = fields.Many2one(
        'res.partner', required=True, tracking=True)
    property_id = fields.Many2one(
        'sa.property', required=True, tracking=True, ondelete='restrict')
    project_id = fields.Many2one(
        related='property_id.project_id', store=True, readonly=True)
    dealer_id = fields.Many2one(
        'sa.property.dealer', string='Dealer', tracking=True)
    salesperson_id = fields.Many2one(
        'res.users', string='Salesperson',
        default=lambda self: self.env.user, tracking=True)

    booking_date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    total_price = fields.Monetary(
        currency_field='currency_id', required=True, tracking=True,
        help="Agreed sale price. Defaults to the property base price.")
    payment_plan_id = fields.Many2one(
        'sa.payment.plan', string='Payment Plan', required=True, tracking=True)
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms',
        default=lambda self: self._default_payment_term(),
        help="Native Odoo payment terms applied to invoices generated for "
             "this booking's installments.")

    installment_ids = fields.One2many(
        'sa.property.installment', 'booking_id', string='Installments',
        copy=False)
    invoice_ids = fields.One2many(
        'account.move', 'sa_booking_id', string='Invoices',
        domain=[('move_type', 'in', ('out_invoice', 'out_refund'))])

    installment_count = fields.Integer(compute='_compute_aggregates', store=False)
    invoice_count = fields.Integer(compute='_compute_aggregates', store=False)
    amount_invoiced = fields.Monetary(
        currency_field='currency_id', compute='_compute_aggregates', store=False)
    amount_paid = fields.Monetary(
        currency_field='currency_id', compute='_compute_aggregates', store=False)
    amount_residual = fields.Monetary(
        currency_field='currency_id', compute='_compute_aggregates', store=False)

    commission_amount = fields.Monetary(
        currency_field='currency_id', compute='_compute_commission', store=True)

    note = fields.Text()

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)',
         'Booking reference must be unique per company.'),
        ('total_price_positive', 'CHECK(total_price > 0)',
         'Total price must be greater than zero.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'sa.property.booking') or _('New')
        return super().create(vals_list)

    def _sa_status_info(self):
        self.ensure_one()
        labels = dict(self._fields['state'].selection)
        return {
            'doc_type': self._sa_doc_type,
            'reference': self.name,
            'status': self.state,
            'status_label': labels.get(self.state, self.state),
            'valid': self.state not in ('cancelled',),
            'rows': [
                (_('Customer'), self.customer_id.name or ''),
                (_('Property'), self.property_id.display_name or ''),
                (_('Project'), self.project_id.name or ''),
                (_('Booking Date'), str(self.booking_date or '')),
                (_('Sale Price'), '%s %s' % (
                    self.currency_id.symbol or '',
                    '{:,.0f}'.format(self.total_price or 0.0))),
            ],
        }

    @api.model
    def _default_payment_term(self):
        ICP = self.env['ir.config_parameter'].sudo()
        term_id = ICP.get_param('sa_property_management.default_payment_term_id')
        if term_id:
            term = self.env['account.payment.term'].browse(int(term_id)).exists()
            return term.id if term else False
        return False

    @api.onchange('property_id')
    def _onchange_property_id(self):
        if self.property_id:
            if not self.total_price:
                self.total_price = self.property_id.base_price
            if self.property_id.currency_id:
                self.currency_id = self.property_id.currency_id

    @api.depends('installment_ids', 'invoice_ids',
                 'invoice_ids.amount_total', 'invoice_ids.amount_residual',
                 'invoice_ids.state')
    def _compute_aggregates(self):
        for rec in self:
            posted = rec.invoice_ids.filtered(lambda m: m.state == 'posted')
            rec.installment_count = len(rec.installment_ids)
            rec.invoice_count = len(rec.invoice_ids)
            rec.amount_invoiced = sum(posted.mapped('amount_total'))
            rec.amount_residual = sum(posted.mapped('amount_residual'))
            rec.amount_paid = rec.amount_invoiced - rec.amount_residual

    @api.depends('total_price', 'dealer_id.commission_percent')
    def _compute_commission(self):
        for rec in self:
            rec.commission_amount = rec.total_price * (
                rec.dealer_id.commission_percent or 0.0) / 100.0

    @api.constrains('property_id', 'state')
    def _check_property_availability(self):
        for rec in self:
            if rec.state in ('confirmed', 'in_payment', 'completed'):
                # No other active booking on this property
                other = self.search([
                    ('id', '!=', rec.id),
                    ('property_id', '=', rec.property_id.id),
                    ('state', 'in', ('confirmed', 'in_payment', 'completed')),
                ], limit=1)
                if other:
                    raise ValidationError(_(
                        "Property '%s' already has active booking '%s'."
                    ) % (rec.property_id.display_name, other.name))

    # ----- Workflow -----

    def action_confirm(self):
        """Mark the booking confirmed; generate the installment schedule and
        the down-payment invoice."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft bookings can be confirmed."))
            if not rec.payment_plan_id:
                raise UserError(_("Select a payment plan first."))
            if rec.property_id.state in ('sold', 'transferred', 'blocked'):
                raise UserError(_(
                    "Property '%s' is not bookable (state: %s)."
                ) % (rec.property_id.display_name, rec.property_id.state))

            rec._generate_installments()
            rec.state = 'confirmed'
            rec.property_id.state = 'booked'
            rec.property_id.current_owner_id = rec.customer_id
            rec._create_invoice_for_first_due()
            rec.state = 'in_payment'

    def action_cancel(self):
        for rec in self:
            if rec.state == 'completed':
                raise UserError(_("Completed bookings cannot be cancelled."))
            # Cancel related draft invoices; refuse if any are posted
            posted = rec.invoice_ids.filtered(lambda m: m.state == 'posted')
            if posted:
                raise UserError(_(
                    "Cannot cancel: %s invoice(s) already posted. Refund them "
                    "individually first."
                ) % len(posted))
            rec.invoice_ids.filtered(lambda m: m.state == 'draft').unlink()
            rec.installment_ids.unlink()
            if rec.property_id.state == 'booked':
                rec.property_id.state = 'available'
                rec.property_id.current_owner_id = False
            rec.state = 'cancelled'

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state != 'cancelled':
                raise UserError(_("Only cancelled bookings can reset to draft."))
            rec.state = 'draft'

    def action_mark_completed(self):
        for rec in self:
            if rec.state != 'in_payment':
                raise UserError(_(
                    "Booking must be in payment to be marked completed."))
            unpaid = rec.installment_ids.filtered(
                lambda i: i.state not in ('paid', 'cancelled'))
            if unpaid:
                raise UserError(_(
                    "%s installment(s) are still unpaid.") % len(unpaid))
            rec.state = 'completed'
            rec.property_id.state = 'sold'

    # ----- Helpers -----

    def _generate_installments(self):
        Installment = self.env['sa.property.installment']
        for rec in self:
            rec.installment_ids.unlink()
            schedule = rec.payment_plan_id.generate_schedule(
                rec.total_price, rec.booking_date)
            for entry in schedule:
                Installment.create({
                    'booking_id': rec.id,
                    'sequence': entry['sequence'],
                    'name': entry['name'],
                    'due_date': entry['due_date'],
                    'amount': entry['amount'],
                    'line_type': entry['line_type'],
                })

    def _get_property_income_account(self):
        """Return the income account to use on generated invoices."""
        self.ensure_one()
        ICP = self.env['ir.config_parameter'].sudo()
        account_id = ICP.get_param('sa_property_management.default_income_account_id')
        if account_id:
            account = self.env['account.account'].browse(int(account_id)).exists()
            if account:
                return account
        # Fallback to the default sales income account
        return self.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_ids', 'in', self.company_id.id),
            ('deprecated', '=', False),
        ], limit=1)

    def _get_sale_journal(self):
        self.ensure_one()
        ICP = self.env['ir.config_parameter'].sudo()
        journal_id = ICP.get_param('sa_property_management.property_journal_id')
        if journal_id:
            journal = self.env['account.journal'].browse(int(journal_id)).exists()
            if journal:
                return journal
        return self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.company_id.id),
        ], limit=1)

    def _create_invoice_for_first_due(self):
        """Issue an invoice for the first unpaid installment."""
        for rec in self:
            first = rec.installment_ids.filtered(
                lambda i: not i.invoice_id
                and i.state in ('pending', 'overdue')).sorted('sequence')[:1]
            if first:
                first.action_generate_invoice()

    def action_view_invoices(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }
        if len(self.invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.invoice_ids.id,
            })
        return action

    def action_view_installments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Installments'),
            'res_model': 'sa.property.installment',
            'view_mode': 'list,form',
            'domain': [('booking_id', '=', self.id)],
        }

    def action_print_payment_schedule(self):
        self.ensure_one()
        return self.env.ref(
            'sa_property_management.action_report_sa_payment_schedule').report_action(self)
