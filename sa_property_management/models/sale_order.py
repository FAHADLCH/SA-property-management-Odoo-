# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sa_booking_id = fields.Many2one(
        'sa.property.booking', string='Property Booking', copy=False, index=True,
        help="Property booking that generated this sale order.")
