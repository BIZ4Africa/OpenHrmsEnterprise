import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Post-migration of ent_loan_accounting 19.0.1.0.6.

    1. Back-fill the loan receivable account on loans created before the
       receivable account existed. Without it the loan cannot be approved any
       more (the disbursement entry needs a receivable account distinct from
       the treasury and from the payroll payable), so this is what keeps an
       existing database workable after the upgrade. The logic lives on the
       model (``hr.loan._backfill_loan_account``) so that it is covered by the
       module tests; this hook only triggers it. Idempotent: 1.0.5 already ran
       it, a loan that carries its account is left untouched.
    2. Optionally arm the payslip recovery. The vendor data creates the 'LO'
       deduction rule on the structure of the company that installed the
       module; the other companies run their own structures and never see it,
       so the loan never amortises on their payslips. Nothing is touched unless
       the company opted in through the configuration parameter below, and a
       structure that already deducts loans through a competing rule code
       (``COMPETING_LOAN_RULE_CODES``, the DRC bridge 'LOAN') is deliberately
       left alone — arming 'LO' next to it would deduct the same installment
       twice.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    filled = env['hr.loan']._backfill_loan_account()
    _logger.info(
        "ent_loan_accounting 19.0.1.0.6: loan account back-filled on %s loan(s).",
        len(filled))

    Structure = env['hr.payroll.structure']
    for company in env['res.company'].search([]):
        parameter = ('ent_loan_accounting.arm_loan_recovery_company_%s'
                     % company.id)
        if env['ir.config_parameter'].sudo().get_param(parameter):
            armed = Structure._arm_loan_recovery_for_company(company)
            _logger.info(
                "ent_loan_accounting 19.0.1.0.6: 'LO' rule armed on %s payroll "
                "structure(s) of company %s.", len(armed),
                company.display_name)
