import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Post-migration of ent_loan_accounting 1.0.7.

    1. Back-fill the loan receivable account on loans created before 1.0.7.
       Without it the loan cannot be approved any more (the disbursement entry
       needs a receivable account distinct from the treasury and from the
       payroll payable), so this is what keeps an existing database workable
       after the upgrade. The logic lives on the model
       (``hr.loan._backfill_loan_account``) so that it is covered by the module
       tests; this hook only triggers it.
    2. Optionally arm the payslip recovery. The vendor data creates the 'LO'
       deduction rule on the structure of the company that installed the
       module; the other companies run their own structures and never see it,
       so the loan never amortises on their payslips. Nothing is touched unless
       the company opted in through the configuration parameter below.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    filled = env['hr.loan']._backfill_loan_account()
    _logger.info(
        "ent_loan_accounting 1.0.7: loan account back-filled on %s loan(s).",
        len(filled))

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
