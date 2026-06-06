# SA Property Management — Pakistan Real Estate (Odoo 18)

End-to-end real estate management module tailored for the Pakistani market.

## Features

- **Project & Property Listing** — Housing societies, blocks, plots, apartments, commercial units.
- **Pakistani Area Units** — Marla, Kanal, Sq.Ft, Sq.Yard, Sq.Meter pre-configured.
- **Payment Plans** — Down payment + N installments (monthly/quarterly/etc.) + balloon payments + on-possession charge.
- **Bookings** — One-click booking confirmation auto-generates installment schedule and customer invoices.
- **Receivables Management** — Installment aging, overdue tracking, integrated with Odoo Accounting.
- **Dealership Management** — Dealers/agents with auto-computed commissions per booking.
- **Property Transfer System** — Owner-change workflow with configurable taxes (CVT, Stamp Duty, Registration Fee, FBR, CGT) and misc charges.
- **Fully Configurable Backend** — Every tax, charge, journal, account and default UoM is data-driven via Settings.
- **Reports** — Booking confirmation, payment schedule, transfer deed.

## Compatibility

- Odoo **18.0** (Community & Enterprise)
- License: **LGPL-3**
- Dependencies: `base`, `mail`, `account`, `product`, `portal`

## Installation (Local Testing)

1. Copy the `sa_property_management` folder into your Odoo `addons` directory
   (or any path declared in `--addons-path`).
2. Start Odoo with the module path:
   ```bash
   ./odoo-bin -c odoo.conf -d test_db -i sa_property_management --without-demo=False
   ```
3. Or install from the UI: **Apps → Update Apps List → search "SA Property Management" → Install**.
4. For a clean local test database:
   ```bash
   ./odoo-bin -c odoo.conf -d sa_test --addons-path=/path/to/addons,./ \
       -i sa_property_management --log-level=info --stop-after-init
   ./odoo-bin -c odoo.conf -d sa_test
   ```

## Running Tests

```bash
./odoo-bin -c odoo.conf -d sa_test_run \
    -i sa_property_management --test-enable --stop-after-init --log-level=test
```

## Quick Tour

1. **Property Management → Configuration → Payment Plans** — create a plan
   (e.g. 20% down, 36 monthly installments, balloon at month 24, 10% on possession).
2. **Property Management → Configuration → Transfer Taxes & Misc Charges** —
   demo data pre-seeds CVT, Stamp Duty, Registration Fee, File Transfer Fee, etc.
3. **Property Management → Projects** — create a project, then add properties.
4. **Property Management → Bookings** — create a booking, attach a payment plan, click **Confirm**.
   The schedule and the first invoice are generated automatically.
5. **Property Management → Receivables** — view all installments with aging.
6. **Property Management → Transfers** — initiate a property transfer, taxes &
   misc charges compute automatically, click **Approve** to finalise.

## Deployment

- Tested locally via the steps above.
- For Odoo.sh: push the module folder to your branch and rebuild.
- For on-premise: drop into `addons/`, restart Odoo, upgrade the module.

## Submission to apps.odoo.com

This module follows the official Odoo Apps guidelines:
- Valid manifest with all required keys (`name`, `version`, `license`, `category`, `summary`).
- LGPL-3 license file included.
- `static/description/index.html` description page with screenshots placeholder.
- No external Python deps; only uses Odoo core modules.
- Semantic version starts with the target Odoo major (`18.0.1.0.0`).
