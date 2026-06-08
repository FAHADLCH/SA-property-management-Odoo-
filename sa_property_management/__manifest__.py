# -*- coding: utf-8 -*-
{
    'name': "SA Property Management",
    'summary': "End-to-end real estate property management for any country: "
               "listings, payment plans, receivables, dealerships and property transfers "
               "with a country-aware tax engine and configurable miscellaneous charges.",
    'description': """
SA Property Management
======================

A complete, **country-agnostic** property / real-estate management solution.
Works out of the box for any market — pick your operating country in the
settings and the matching transfer taxes and charges are applied automatically.

Key Features
------------
* **Property Listing** with flexible Units of Measure (Sq.Ft, Sq.Meter,
  Sq.Yard, plus regional units such as Marla and Kanal).
* **Project / Housing Society** management with blocks, streets and plot numbers.
* **Payment Plan Builder** (Down Payment + Monthly/Quarterly/Half-Yearly/Yearly
  installments + Balloon Payments + On-Possession charge).
* **Booking Workflow** that auto-generates the installment schedule and
  customer invoices through standard Odoo Accounting.
* **Receivables Management** with installment aging, overdue tracking and
  registered payment integration.
* **Property Dealership Management** with commission calculation per booking.
* **Country-Aware Tax Engine** — define transfer taxes (transfer/stamp duty,
  registration, capital gains, VAT/GST, withholding, etc.) and miscellaneous
  charges per country, then select the relevant country in Configuration.
  Ready-made presets ship for several markets and you can add your own.
* **Backend Configuration** for default tax accounts, journals, currency,
  operating country and area unit-of-measure - everything is data-driven,
  with no hard-coded country logic.

Built On
--------
Leverages Odoo core: ``account``, ``product``, ``mail``, ``portal`` and
``crm`` for invoicing, communications, customer self-service and lead-source
integration. No external Python dependencies — deploys on Odoo.sh and
on-premise (Community or Enterprise).

Compatibility
-------------
Verified on **Odoo 18.0 and 19.0** (Community).
    """,
    'author': "SA Systems",
    'maintainer': "SA Systems",
    'website': "https://sasystems.solutions/custom-web-app-development",
    'support': "info@sasystems.solutions",
    'license': 'LGPL-3',
    'category': 'Services/Real Estate',
    # Free app: no price/currency keys so the Odoo Apps store lists it as free.
    # Series-prefixed version (this is the Odoo 19.0 branch).
    'version': '19.0.1.0.0',
    'application': True,
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',

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
