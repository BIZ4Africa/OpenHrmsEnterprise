# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################
from odoo import api, models

import logging

_logger = logging.getLogger(__name__)

LOAN_RULE_CODE = 'LO'

# Rule codes that already deduct a loan/advance from the payslip. When a
# structure carries one of them, arming the OpenHRMS 'LO' rule on that same
# structure would deduct the same installment twice. Measured on the SPORTS
# EXPERTS instance (2026-10-08): the DRC payroll bridge
# ``l10n_cd_hr_payroll_loan_bridge`` aggregates the unpaid installments into a
# 'LOAN' payslip input, consumed by a 'LOAN' salary rule — so the OpenHRMS
# route must not be armed next to it.
COMPETING_LOAN_RULE_CODES = ('LOAN',)


class HrPayrollStructure(models.Model):
    """Arm the loan deduction rule on a company's payroll structures.

    ``ent_ohrms_loan`` creates the ``LO`` deduction rule on a single structure,
    created for the company that installed the module. On a multi-company
    database the other companies run their own structures (usually copies),
    which never carry that rule: ``hr.payslip.compute_sheet`` then finds no
    ``LO`` rule, never adds the loan input line, and the recovery entry is
    never posted — the loan never amortises on the payslips.

    ``_arm_loan_recovery`` copies the reference ``LO`` rule definition onto the
    structures it is called on. It is idempotent: a structure that already
    carries an ``LO`` rule is left untouched. The rule only produces an amount
    when a loan input line exists, so arming a structure is inert for every
    employee without an approved loan.
    """
    _inherit = 'hr.payroll.structure'

    def _loan_recovery_rule(self):
        """Return the existing ``LO`` rule of this structure, if any."""
        self.ensure_one()
        return self.env['hr.salary.rule'].search([
            ('code', '=', LOAN_RULE_CODE),
            ('struct_id', '=', self.id),
        ], limit=1)

    def _competing_loan_rule(self):
        """Return the loan deduction rule already present on this structure.

        A structure that deducts loans through another code (the DRC payroll
        bridge uses ``LOAN``) must not receive the OpenHRMS ``LO`` rule: both
        would deduct the same installment.
        """
        self.ensure_one()
        return self.env['hr.salary.rule'].search([
            ('code', 'in', list(COMPETING_LOAN_RULE_CODES)),
            ('struct_id', '=', self.id),
        ], limit=1)

    def _arm_loan_recovery(self):
        """Ensure each structure carries the ``LO`` rule. Idempotent.

        A structure that already deducts loans through a competing rule code
        (``COMPETING_LOAN_RULE_CODES``) is deliberately left alone.
        """
        Rule = self.env['hr.salary.rule']
        created = Rule.browse()
        template = Rule.search([('code', '=', LOAN_RULE_CODE)], limit=1)
        if not template:
            return created
        for structure in self:
            if structure._loan_recovery_rule():
                continue
            competing = structure._competing_loan_rule()
            if competing:
                _logger.warning(
                    "ent_loan_accounting: payroll structure %s already deducts "
                    "loans through rule(s) %s — the 'LO' rule is NOT armed "
                    "there, it would deduct the same installment twice.",
                    structure.display_name,
                    ', '.join(competing.mapped('code')))
                continue
            created |= template.copy({
                'struct_id': structure.id,
                'company_id': structure.company_id.id or False,
            })
        return created

    @api.model
    def _arm_loan_recovery_for_company(self, company):
        """Arm the ``LO`` rule on every payroll structure of ``company``."""
        structures = self.search([('company_id', '=', company.id)])
        return structures._arm_loan_recovery()
