import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Post-migration of ent_loan_accounting 1.0.5.

    Back-fill the loan receivable account on loans created before 1.0.5.
    Without it the loan cannot be approved any more (the disbursement entry
    needs a receivable account distinct from the treasury and from the payroll
    payable), so this is what keeps an existing database workable after the
    upgrade. The logic lives on the model
    (``hr.loan._backfill_loan_account``) so that it is covered by the module
    tests; this hook only triggers it.

    The 18.0 work this version ports (``ent_loan_accounting 18.0.1.0.7``) also
    armed the 'LO' payslip deduction rule, opt-in per company through
    ``ent_loan_accounting.arm_loan_recovery_company_<company_id>``, on top of
    its own ``models/hr_payroll_structure.py``. That part is NOT ported here —
    it is a distinct concern (making the recovery reach companies that do not
    run the vendor structure), it needs the 19.0 ``hr.payroll.structure`` API
    to be checked, and porting the accounting DIRECTION does not need it.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    filled = env['hr.loan']._backfill_loan_account()
    _logger.info(
        "ent_loan_accounting 1.0.5: loan account back-filled on %s loan(s).",
        len(filled))
