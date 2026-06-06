# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaPropertyFeature(models.Model):
    _name = 'sa.property.feature'
    _description = 'Property Feature'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    color = fields.Integer()

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Feature name must be unique.'),
    ]


class SaProperty(models.Model):
    """An individual property unit — plot, apartment, house or commercial unit."""
    _name = 'sa.property'
    _description = 'Property Unit'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sa.qr.mixin']
    _order = 'project_id, code'
    _rec_name = 'display_name'

    _sa_doc_type = _('Property File')

    name = fields.Char(string='Title', required=True, tracking=True)
    code = fields.Char(string='Reference', required=True, copy=False,
                       default=lambda self: _('New'), tracking=True)
    display_name = fields.Char(compute='_compute_display_name', store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.company.currency_id,
        help="Pricing currency for this unit. Defaults from the project.")

    project_id = fields.Many2one(
        'sa.property.project', string='Project', required=True,
        ondelete='restrict', tracking=True, index=True)

    property_type = fields.Selection(
        [('plot', 'Plot'),
         ('house', 'House'),
         ('apartment', 'Apartment'),
         ('shop', 'Shop'),
         ('commercial', 'Commercial Unit'),
         ('office', 'Office')],
        default='plot', required=True, tracking=True)

    # Pakistani location detail
    block = fields.Char(tracking=True)
    street = fields.Char()
    plot_number = fields.Char(tracking=True)
    floor = fields.Char()
    facing = fields.Selection(
        [('north', 'North'),
         ('south', 'South'),
         ('east', 'East'),
         ('west', 'West'),
         ('north_east', 'North-East'),
         ('north_west', 'North-West'),
         ('south_east', 'South-East'),
         ('south_west', 'South-West')])
    location_premium = fields.Selection(
        [('none', 'None'),
         ('corner', 'Corner'),
         ('park_facing', 'Park-Facing'),
         ('main_road', 'Main Road'),
         ('main_boulevard', 'Main Boulevard'),
         ('corner_park', 'Corner + Park-Facing')],
        default='none')

    area = fields.Float(string='Area', required=True, tracking=True)
    area_uom = fields.Selection(
        [('marla', 'Marla'),
         ('kanal', 'Kanal'),
         ('sqft', 'Square Foot'),
         ('sqyd', 'Square Yard'),
         ('sqm', 'Square Meter')],
        required=True, default='marla', tracking=True)
    covered_area = fields.Float(string='Covered Area (Sq.Ft)')

    bedrooms = fields.Integer()
    bathrooms = fields.Integer()
    parking_spaces = fields.Integer()
    feature_ids = fields.Many2many('sa.property.feature', string='Features')

    base_price = fields.Monetary(currency_field='currency_id', tracking=True)
    price_per_unit_area = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_price_per_unit_area', store=True)
    dc_value = fields.Monetary(
        currency_field='currency_id',
        help="DC (Deputy Commissioner) notified value used for FBR/CVT tax base.")

    image = fields.Image(max_width=1920, max_height=1920)
    description = fields.Html()

    image_ids = fields.One2many(
        'sa.property.image', 'property_id', string='Gallery')
    collateral_ids = fields.One2many(
        'sa.marketing.collateral', 'property_id', string='Marketing Collateral')
    service_assignment_ids = fields.One2many(
        'sa.property.service.assignment', 'property_id', string='Service Billing')

    state = fields.Selection(
        [('draft', 'Draft'),
         ('available', 'Available'),
         ('reserved', 'Reserved'),
         ('booked', 'Booked'),
         ('sold', 'Sold'),
         ('transferred', 'Transferred'),
         ('blocked', 'Blocked')],
        default='draft', required=True, tracking=True, copy=False)

    current_owner_id = fields.Many2one(
        'res.partner', string='Current Owner', tracking=True, copy=False)
    booking_ids = fields.One2many(
        'sa.property.booking', 'property_id', string='Bookings')
    booking_count = fields.Integer(
        compute='_compute_counts', store=False)
    transfer_ids = fields.One2many(
        'sa.property.transfer', 'property_id', string='Transfers')
    transfer_count = fields.Integer(
        compute='_compute_counts', store=False)

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)',
         'Property reference must be unique per company.'),
        ('area_positive', 'CHECK(area > 0)', 'Area must be greater than zero.'),
        ('base_price_positive', 'CHECK(base_price >= 0)',
         'Base price cannot be negative.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('New')) == _('New'):
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    'sa.property') or _('New')
        return super().create(vals_list)

    @api.depends('name', 'code', 'project_id')
    def _compute_display_name(self):
        for rec in self:
            parts = [rec.code or '', rec.name or '']
            rec.display_name = ' - '.join(p for p in parts if p)

    @api.onchange('project_id')
    def _onchange_project_id_currency(self):
        if self.project_id and self.project_id.currency_id:
            self.currency_id = self.project_id.currency_id

    def _sa_status_info(self):
        self.ensure_one()
        labels = dict(self._fields['state'].selection)
        return {
            'doc_type': self._sa_doc_type,
            'reference': self.display_name,
            'status': self.state,
            'status_label': labels.get(self.state, self.state),
            'valid': self.state not in ('blocked', 'draft'),
            'rows': [
                (_('Project'), self.project_id.name or ''),
                (_('Type'), dict(self._fields['property_type'].selection).get(
                    self.property_type, '')),
                (_('Area'), '%s %s' % (
                    self.area or 0.0,
                    dict(self._fields['area_uom'].selection).get(self.area_uom, ''))),
                (_('Current Owner'), self.current_owner_id.name or _('—')),
            ],
        }

    @api.depends('base_price', 'area')
    def _compute_price_per_unit_area(self):
        for rec in self:
            rec.price_per_unit_area = (
                rec.base_price / rec.area if rec.area else 0.0)

    @api.depends('booking_ids', 'transfer_ids')
    def _compute_counts(self):
        for rec in self:
            rec.booking_count = len(rec.booking_ids)
            rec.transfer_count = len(rec.transfer_ids)

    @api.constrains('state', 'current_owner_id')
    def _check_owner_required(self):
        for rec in self:
            if rec.state in ('sold', 'transferred') and not rec.current_owner_id:
                raise ValidationError(_(
                    "Property '%s' is %s but has no owner set."
                ) % (rec.display_name, rec.state))

    def action_set_available(self):
        for rec in self:
            if rec.state in ('booked', 'sold', 'transferred'):
                raise ValidationError(_(
                    "Cannot mark '%s' available: it is currently %s."
                ) % (rec.display_name, rec.state))
            rec.state = 'available'

    def action_block(self):
        for rec in self:
            if rec.state in ('booked', 'sold', 'transferred'):
                raise ValidationError(_(
                    "Cannot block '%s' while it is %s."
                ) % (rec.display_name, rec.state))
            rec.state = 'blocked'

    def action_view_bookings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bookings - %s', self.display_name),
            'res_model': 'sa.property.booking',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    def action_view_transfers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Transfers - %s', self.display_name),
            'res_model': 'sa.property.transfer',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }
