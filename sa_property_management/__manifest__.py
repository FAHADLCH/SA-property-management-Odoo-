# -*- coding: utf-8 -*-
{
    'name': "SA Property Management - Pakistan Real Estate",
    'summary': "End-to-end real estate property management for the Pakistani market: "
               "listings, payment plans, receivables, dealerships and property transfers "
               "with CVT, Stamp Duty, FBR tax and misc-charge configuration.",
    'description': """
SA Property Management
======================

A complete property/real-estate management solution tailored for the
**Pakistani real estate market**.

Key Features
------------
* **Property Listing** with Pakistani Units of Measure (Marla, Kanal, Sq.Ft, Sq.Yard).
* **Project / Housing Society** management with blocks, streets and plot numbers.
* **Payment Plan Builder** (Down Payment + Monthly/Quarterly/Half-Yearly/Yearly
  installments + Balloon Payments + On-Possession charge).
* **Booking Workflow** that auto-generates the installment schedule and
  customer invoices through standard Odoo Accounting.
* **Receivables Management** with installment aging, overdue tracking and
  registered payment integration.
* **Property Dealership Management** with commission calculation per booking.
* **Property Transfer System** with configurable Taxes (CVT, Stamp Duty,
  Registration Fee, Capital Gains, FBR) and Miscellaneous Charges
  (file transfer, society dues, utility transfer).
* **Backend Configuration** for all default tax accounts, journals, currency
  (PKR) and area unit-of-measure - everything is data-driven, no hard-coding.

Built On
--------
Leverages Odoo core: ``account``, ``product``, ``mail`` and ``portal`` for
invoicing, communications and customer self-service.
    """,
    'author': "SA Property Management",
    'maintainer': "SA Property Management",
    'website': "https://example.com",
    'support': "support@example.com",
    'license': 'LGPL-3',
    'category': 'Services/Real Estate',
    'version': '18.0.1.0.0',
    'application': True,
    'installable': True,
    'auto_install': False,

    'depends': [
        'base',
        'mail',
        'account',
        'product',
        'portal',
        'crm',
    ],

    'data': [
        # security
        'security/sa_property_security.xml',
        'security/ir.model.access.csv',
        # data
        'data/ir_sequence_data.xml',
        'data/property_area_uom_data.xml',
        'data/transfer_tax_data.xml',
        'data/misc_charge_data.xml',
        'data/service_data.xml',
        # wizards
        'wizards/sa_booking_confirm_wizard_views.xml',
        'wizards/sa_installment_payment_wizard_views.xml',
        'wizards/sa_property_transfer_wizard_views.xml',
        'wizards/sa_lead_import_wizard_views.xml',
        # reports
        'reports/report_paperformat.xml',
        'reports/sa_booking_report.xml',
        'reports/sa_payment_schedule_report.xml',
        'reports/sa_transfer_deed_report.xml',
        'reports/sa_qr_reports.xml',
        # views
        'views/sa_transfer_tax_views.xml',
        'views/sa_misc_charge_views.xml',
        'views/res_partner_views.xml',
        'views/sa_payment_plan_views.xml',
        'views/sa_property_project_views.xml',
        'views/sa_property_views.xml',
        'views/sa_property_dealer_views.xml',
        'views/sa_property_installment_views.xml',
        'views/sa_property_booking_views.xml',
        'views/sa_property_transfer_views.xml',
        'views/sa_property_service_views.xml',
        'views/sa_dealer_allocation_views.xml',
        'views/sa_lead_source_views.xml',
        'views/sa_crm_lead_views.xml',
        'views/sa_verify_templates.xml',
        'views/res_config_settings_views.xml',
        'views/sa_property_dashboard_views.xml',
        'views/menus.xml',
    ],

    'demo': [
        'demo/demo_data.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'sa_property_management/static/src/scss/sa_property_dashboard.scss',
            'sa_property_management/static/src/js/sa_property_dashboard.js',
            'sa_property_management/static/src/xml/sa_property_dashboard.xml',
        ],
    },

    'images': [
        'static/description/banner.png',
    ],
}
