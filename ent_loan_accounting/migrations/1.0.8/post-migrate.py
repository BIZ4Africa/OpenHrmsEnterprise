import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Post-migration of ent_loan_accounting 1.0.8 — trace only, no reposting.

    From 1.0.8 on, a loan expressed in a currency other than the company
    currency produces a disbursement entry converted at the rate of the entry
    date (and carrying the loan currency), like the payslip entry that recovers
    the installments. Entries posted before 1.0.8 are **left untouched**: the
    amounts, accounts, dates and balances stay exactly as they are. Correcting
    an already posted entry is an accounting decision, not a technical one.

    This hook only reports them, through the read-only model helper
    ``hr.loan._loans_with_unconverted_disbursement`` (idempotent: it writes
    nothing, it can be replayed at will).

    The two new settings (``res.company.ent_loan_currency_conversion``,
    ``res.company.ent_loan_conversion_date``) need no backfill and get none
    here: Odoo initialises a *new* column on the existing rows with the field
    default (``update_db_notnull`` -> ``models._init_column`` — the Boolean
    column is created nullable, without SQL DEFAULT, because
    ``Boolean._column_type`` is ``'bool'``). Measured on a throwaway Odoo 18
    database: the columns dropped, a plain ``-u ent_loan_accounting`` without
    any version change (so this hook cannot run) restores
    ``ent_loan_currency_conversion = true`` and
    ``ent_loan_conversion_date = 'move_date'`` on the existing company row,
    with ``res_company.write_date`` untouched (raw SQL, not an ORM write).
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
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
