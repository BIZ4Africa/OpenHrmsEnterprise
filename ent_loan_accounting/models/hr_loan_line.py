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
from odoo import fields, models
from odoo.exceptions import UserError


class HrLoanLine(models.Model):
    """ Creates an invoice for loans. """
    _inherit = "hr.loan.line"

    def action_paid_amount(self, month):
        """
            This creates the account move line for payment of each installment.

            Correct direction: **debit the payroll payable (the installment is
            deducted from the salary, so what the company owes the employee
            decreases), credit the loan receivable (the employee's debt
            decreases)**. The vendor release credited the treasury, which
            credited the bank a second time.

            Unit: the installment is an amount of the loan currency; the entry
            is converted into the company currency at the rate of the entry
            date, and carries the loan currency when the journal allows it —
            same rule as the disbursement entry (``hr.loan``).

            Name: the entry NUMBER belongs to the journal (``BNK1/2026/00005``)
            and is **not** forced any more. The module used to write
            ``'LOAN/ <employee>/<month>'`` on it, which the account sequence
            mixin rejects as soon as a group of digits of the label does not
            match the entry date, and which made the journal adopt the label as
            its numbering template for the entries that follow (measured on
            SPORTS EXPERTS, journal BNK1 — see
            ``hr.loan._loan_recovery_move_ref``). The human label lives in
            ``ref`` and on the entry lines.
        """
        for line in self:
            if line.loan_id.state != 'approve':
                raise UserError("Loan Request must be approved")
            loan = line.loan_id
            loan._check_loan_accounts()
            on_date = fields.Date.context_today(line)
            amount = line.amount
            company_amount = loan._loan_company_currency_amount(amount, on_date)
            carries_currency = loan._loan_carries_currency()
            partner_id = line.employee_id.work_contact_id.id or False
            line_name = ' '.join(
                part for part in
                ('Loan', loan.name, line.employee_id.name, month) if part)

            def _line_vals(account_id, debit, credit, amount_currency, partner):
                vals = {
                    'name': line_name,
                    'account_id': account_id,
                    'journal_id': loan.journal_id.id,
                    'date': on_date,
                    'debit': debit,
                    'credit': credit,
                }
                if partner:
                    vals['partner_id'] = partner
                if carries_currency:
                    vals['currency_id'] = loan.currency_id.id
                    vals['amount_currency'] = amount_currency
                return vals

            debit_vals = _line_vals(
                loan.employee_account_id.id,
                company_amount > 0.0 and company_amount or 0.0,
                company_amount < 0.0 and -company_amount or 0.0,
                amount, partner_id)
            credit_vals = _line_vals(
                loan.loan_account_id.id,
                company_amount < 0.0 and -company_amount or 0.0,
                company_amount > 0.0 and company_amount or 0.0,
                -amount, partner_id)
            vals = {
                # NO free 'name' here on purpose: the entry number belongs to
                # the journal ('BNK1/2026/00005'). account.sequence_mixin reads
                # a name as a *sequence* — a forced label is refused by
                # _constrains_date_sequence when its digits do not match the
                # entry date, and the journal then adopts that label as its
                # numbering TEMPLATE for every following entry.
                'narration': line.employee_id.name,
                'ref': loan._loan_recovery_move_ref(month,
                                                    line.employee_id.name),
                'journal_id': loan.journal_id.id,
                'date': on_date,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            if carries_currency:
                vals['currency_id'] = loan.currency_id.id
            move = self.env['account.move'].create(vals)
            move.action_post()
        return True
