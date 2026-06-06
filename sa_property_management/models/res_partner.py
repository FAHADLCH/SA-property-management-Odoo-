# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'sa.qr.mixin']

    _sa_doc_type = _('Customer File')

    # --- Identity (Pakistan) ---
    sa_cnic = fields.Char(string='CNIC',
                          help="Pakistani National Identity Card number "
                               "(format: 12345-1234567-1).")
    sa_ntn = fields.Char(string='NTN',
                         help="National Tax Number issued by FBR.")
    sa_passport_no = fields.Char(string='Passport No.')
    sa_father_husband_name = fields.Char(
        string='Father / Husband Name',
        help="Guardian name as printed on the CNIC.")
    sa_dob = fields.Date(string='Date of Birth')
    sa_gender = fields.Selection(
        [('male', 'Male'),
         ('female', 'Female'),
         ('other', 'Other')],
        string='Gender')
    sa_nationality = fields.Char(string='Nationality', default='Pakistani')
    sa_occupation = fields.Char(string='Occupation')

    sa_is_property_customer = fields.Boolean(string='Property Customer')
    sa_is_property_dealer = fields.Boolean(string='Is Property Dealer')
    sa_dealer_id = fields.Many2one(
        'sa.property.dealer', string='Dealer Record',
        compute='_compute_sa_dealer_id', store=False)

    # --- Next of Kin ---
    sa_nok_name = fields.Char(string='Next of Kin Name')
    sa_nok_relation = fields.Selection(
        [('father', 'Father'),
         ('mother', 'Mother'),
         ('spouse', 'Spouse'),
         ('son', 'Son'),
         ('daughter', 'Daughter'),
         ('brother', 'Brother'),
         ('sister', 'Sister'),
         ('other', 'Other')],
        string='Relationship')
    sa_nok_cnic = fields.Char(string='Next of Kin CNIC')
    sa_nok_mobile = fields.Char(string='Next of Kin Mobile')
    sa_nok_phone = fields.Char(string='Next of Kin Telephone')
    sa_nok_address = fields.Text(string='Next of Kin Address')

    def _compute_sa_dealer_id(self):
        Dealer = self.env['sa.property.dealer']
        for rec in self:
            rec.sa_dealer_id = Dealer.search(
                [('partner_id', '=', rec.id)], limit=1)

    def _sa_status_info(self):
        self.ensure_one()
        return {
            'doc_type': self._sa_doc_type,
            'reference': self.name or '',
            'status': 'verified',
            'status_label': _('Verified'),
            'valid': True,
            'rows': [
                (_('CNIC'), self.sa_cnic or _('—')),
                (_('Father / Husband'), self.sa_father_husband_name or _('—')),
                (_('Mobile'), self.mobile or self.phone or _('—')),
                (_('City'), self.city or _('—')),
            ],
        }
