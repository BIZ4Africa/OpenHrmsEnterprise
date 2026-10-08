import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# Account codes of the loan receivable (employee advance / "personnel, avances")
# in the SYSCOHADA / OHADA charts used by the BIZ4A instances. This migration
# only *locates* an existing account: it never creates one.
LOAN_ACCOUNT_CODES = ('421100', '4211')


def _find_loan_account(env, company):
    Account = env['account.account'].with_company(company)
    for code in LOAN_ACCOUNT_CODES:
        account = Account.search([('code', '=', code)], limit=1)
        if account:
            return account
    return Account.browse()


def migrate(cr, version):
    """Back-fill the loan receivable account on loans created before 1.0.7.

    Without it the loan cannot be approved any more (the disbursement entry
    needs a receivable account distinct from the treasury and from the payroll
    payable), so the migration is what keeps an existing database workable
    after the module upgrade.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    Loan = env['hr.loan']
    loans = Loan.search([('loan_account_id', '=', False)])
    filled, skipped = 0, 0
    for loan in loans:
        if not loan.company_id:
            skipped += 1
            continue
        account = _find_loan_account(env, loan.company_id)
        if not account:
            _logger.warning(
                "ent_loan_accounting 1.0.7: no loan receivable account found "
                "for company %s (tried codes %s) — loan %s (%s) is left "
                "without a loan account and cannot be approved until one is "
                "set.", loan.company_id.display_name, LOAN_ACCOUNT_CODES,
                loan.id, loan.name)
            skipped += 1
            continue
        loan.loan_account_id = account.id
        filled += 1
    _logger.info(
        "ent_loan_accounting 1.0.7: loan account back-filled on %s loan(s), "
        "%s skipped.", filled, skipped)

    # Optional arming of the payslip recovery. The vendor data creates the 'LO'
    # deduction rule on the structure of the company that installed the module;
    # the other companies run their own structures and never see it, so the
    # loan never amortises on their payslips. Nothing is touched unless the
    # company opted in through the configuration parameter below.
    Structure = env['hr.payroll.structure']
    for company in env['res.company'].search([]):
        parameter = ('ent_loan_accounting.arm_loan_recovery_company_%s'
                     % company.id)
        if env['ir.config_parameter'].sudo().get_param(parameter):
            armed = Structure._arm_loan_recovery_for_company(company)
            _logger.info(
                "ent_loan_accounting 1.0.7: 'LO' rule armed on %s payroll "
                "structure(s) of company %s.", len(armed),
                company.display_name)
