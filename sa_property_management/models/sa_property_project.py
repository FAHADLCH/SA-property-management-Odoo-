# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaPropertyProject(models.Model):
    """Top-level grouping for properties — a housing society, tower or scheme."""
    _name = 'sa.property.project'
    _description = 'Property Project / Society'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.company.currency_id,
        help="Default pricing currency for properties in this project.")

    city = fields.Char(tracking=True)
    state_id = fields.Many2one('res.country.state', string='Province',
                               domain="[('country_id.code', '=', 'PK')]")
    country_id = fields.Many2one(
        'res.country', default=lambda self: self.env.ref('base.pk', raise_if_not_found=False))
    address = fields.Text()

    total_area = fields.Float(string='Total Land Area')
    area_uom = fields.Selection(
        [('marla', 'Marla'),
         ('kanal', 'Kanal'),
         ('sqft', 'Square Foot'),
         ('sqyd', 'Square Yard'),
         ('sqm', 'Square Meter'),
         ('acre', 'Acre')],
        default='kanal', required=True)

    description = fields.Html()
    image = fields.Image(max_width=1024, max_height=1024)

    image_ids = fields.One2many(
        'sa.property.image', 'project_id', string='Gallery')
    collateral_ids = fields.One2many(
        'sa.marketing.collateral', 'project_id', string='Marketing Collateral')

    dealer_ids = fields.Many2many(
        'sa.property.dealer', string='Assigned Dealers')
    property_ids = fields.One2many(
        'sa.property', 'project_id', string='Properties')

    property_count = fields.Integer(
        compute='_compute_property_stats', store=False)
    available_count = fields.Integer(
        compute='_compute_property_stats', store=False)
    sold_count = fields.Integer(
        compute='_compute_property_stats', store=False)

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)',
         'Project code must be unique per company.'),
    ]

    @api.depends('property_ids', 'property_ids.state')
    def _compute_property_stats(self):
        for rec in self:
            rec.property_count = len(rec.property_ids)
            rec.available_count = len(rec.property_ids.filtered(
                lambda p: p.state == 'available'))
            rec.sold_count = len(rec.property_ids.filtered(
                lambda p: p.state in ('sold', 'transferred')))

    def action_view_properties(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'sa.property',
            'view_mode': 'kanban,list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }
