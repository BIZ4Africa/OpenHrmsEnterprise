import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def activate_currency_conversion(env):
    """Give existing companies the declared default of the new switch.

    ``ent_loan_currency_conversion`` is a Boolean created by this version, so
    Odoo adds the column with ``DEFAULT false`` and never backfills it: the
    framework only initialises the rows that are still NULL
    (``odoo/fields.py::update_db_notnull`` -> ``odoo/models.py::_init_column``
    -> ``UPDATE ... WHERE <field> IS NULL``). A Boolean column is never NULL,
    so the field's ``default=True`` would NOT reach a company that already
    exists — and the fix would be silently inert on the client instance.

    The switch did not exist before 1.0.8, so no company can hold an explicit
    choice at this point: enabling it here is simply the declared default.
    Idempotent (the post-migration runs once, and it writes nothing when the
    switch is already on); no accounting entry is ever touched.

    Returns the companies that were switched on.
    """
    companies = env['res.company'].sudo().search([
        ('ent_loan_currency_conversion', '=', False),
    ])
    if companies:
        companies.write({'ent_loan_currency_conversion': True})
        _logger.info(
            "ent_loan_accounting 1.0.8: loan disbursement conversion enabled "
            "on %s company(ies): %s (declared default of the new switch; the "
            "column is created with DEFAULT false and Odoo does not backfill "
            "Boolean columns).",
            len(companies), ', '.join(companies.mapped('display_name')))
    return companies


def migrate(cr, version):
    """Post-migration of ent_loan_accounting 1.0.8.

    Two things, and nothing else:

    1. **Configuration** — switch on the currency conversion for the companies
       that exist (``activate_currency_conversion``): the declared default,
       which the framework does not apply to a Boolean column created on an
       existing table. Without it the fix ships but stays inert.

    2. **Trace only, no reposting** — from 1.0.8 on, a loan expressed in a
       currency other than the company currency produces a disbursement entry
       converted at the rate of the entry date (and carrying the loan
       currency), like the payslip entry that recovers the installments.
       Entries posted before 1.0.8 are **left untouched**: amounts, accounts,
       dates and balances stay exactly as they are. Correcting an already
       posted entry is an accounting decision, not a technical one. The hook
       only reports them, through the read-only model helper
       ``hr.loan._loans_with_unconverted_disbursement`` (idempotent: it writes
       nothing, it can be replayed at will).
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    activate_currency_conversion(env)

    loans = env['hr.loan']._loans_with_unconverted_disbursement()

    for loan in loans:
        _logger.warning(
            "ent_loan_accounting 1.0.8: loan %s (company %s) is expressed in "
            "%s but its posted disbursement entry %s is in %s — pre-1.0.8 "
            "posting, left untouched. A correction entry is a separate "
            "accounting decision.",
            loan.name, loan.company_id.display_name,
            loan.currency_id.display_name, loan.move_id.name,
            loan.move_id.currency_id.display_name)

    _logger.info(
        "ent_loan_accounting 1.0.8: %s pre-existing loan disbursement(s) "
        "reported as not expressed in the loan currency; none was reposted.",
        len(loans))
