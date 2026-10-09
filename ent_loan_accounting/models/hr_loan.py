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
from datetime import date
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Account codes of the loan receivable ("personnel, avances") in the SYSCOHADA /
# OHADA charts used by the BIZ4A instances. The module only *locates* an
# existing account: it never creates one.
LOAN_ACCOUNT_CODES = ('421100', '4211')


class HrLoan(models.Model):
    """ Inheriting hr.loan for adding fields into the model. """
    _inherit = 'hr.loan'

    employee_account_id = fields.Many2one(comodel_name='account.account',
                                          string="Employee Account",
                                          help="Payroll payable account "
                                               "(salary due to the employee). "
                                               "Debited when the installment is "
                                               "recovered on a payslip. Select "
                                               "the employee chart of accounts")
    treasury_account_id = fields.Many2one(comodel_name='account.account',
                                          string="Treasury Account",
                                          help="Bank/cash account that "
                                               "disburses the loan. Credited on "
                                               "disbursement. Select employee "
                                               "treasury account details")
    loan_account_id = fields.Many2one(comodel_name='account.account',
                                      string="Loan Account",
                                      help="Receivable account carrying the "
                                           "employee loan while it is being "
                                           "repaid: debited on disbursement, "
                                           "credited on each payslip recovery. "
                                           "Must be a different account from "
                                           "the employee and treasury accounts")
    journal_id = fields.Many2one(comodel_name='account.journal',
                                 string="Journal",
                                 help="Select journal for employee")
    move_id = fields.Many2one(comodel_name='account.move',
                              string="Accounting Entry",
                              readonly=True,
                              help="Related journal entry for this loan")
    state = fields.Selection(
        selection_add=[('waiting_approval_2', 'Waiting Approval'), ('approve',)],
        ondelete={'waiting_approval_2': 'set default'},
    )

    @api.model
    def _find_loan_account(self, company):
        """Locate the loan receivable account of a company (never creates)."""
        Account = self.env['account.account'].with_company(company)
        for code in LOAN_ACCOUNT_CODES:
            account = Account.search([('code', '=', code)], limit=1)
            if account:
                return account
        return Account.browse()

    @api.model
    def _backfill_loan_account(self):
        """Set the loan receivable account on every loan missing it.

        Idempotent: a loan that already carries a loan account is left
        untouched. Called by ``migrations/1.0.7/post-migrate.py`` so that an
        upgraded database stays workable — without a receivable account a loan
        cannot be approved any more.
        """
        filled = self.browse()
        for loan in self.search([('loan_account_id', '=', False)]):
            if not loan.company_id:
                continue
            account = self._find_loan_account(loan.company_id)
            if not account:
                _logger.warning(
                    "ent_loan_accounting 1.0.7: no loan receivable account "
                    "found for company %s (tried codes %s) — loan %s is left "
                    "without a loan account and cannot be approved until one "
                    "is set.", loan.company_id.display_name,
                    LOAN_ACCOUNT_CODES, loan.name)
                continue
            loan.loan_account_id = account.id
            filled |= loan
        return filled

    def _check_loan_accounts(self):
        """ The three accounts of a loan are distinct by construction: the loan
        receivable cannot be the treasury nor the payroll payable account.
        """
        self.ensure_one()
        if (not self.employee_account_id or not self.treasury_account_id or
                not self.loan_account_id or not self.journal_id):
            raise UserError(
                "You must enter employee account & Treasury account, Loan "
                "account and journal to approve ")
        accounts = (self.employee_account_id + self.treasury_account_id +
                    self.loan_account_id)
        if len(accounts) != 3:
            raise UserError(
                "The Employee account, the Treasury account and the Loan "
                "account must be three different accounts: a loan needs a "
                "receivable account distinct from the treasury and from the "
                "payroll payable.")

    # ------------------------------------------------------------------
    # Accounting unit of the disbursement entry ('octroi')
    # ------------------------------------------------------------------
    # A loan is a document expressed in its own currency
    # (``hr.loan.currency_id``, in practice the employee contract currency),
    # while the company books are kept in the company currency. The payslip
    # entry that recovers an installment converts the legal currency into the
    # company currency (``res.company.convert_from_legal_currency``); the
    # disbursement entry must do the same. Posted raw, the receivable is
    # expressed in the wrong unit and no installment can ever close it.
    #
    # Measured on SPORTS EXPERTS 2026-10-09 (company 2 in USD, loan in CDF at
    # 2 265 CDF/USD): the entry was D 421100 300 000 / C 521001 300 000 in USD
    # for a 300 000 CDF loan (132,45 USD), while the recovery posted 44,15 USD
    # per installment — 299 867,55 USD of the receivable could never be settled
    # (card t_c6e17a81).

    def _loan_disbursement_date(self):
        """Date carried by the disbursement entry, and date of its rate.

        Parametrable: ``res.company.ent_loan_conversion_date`` selects the
        accounting entry date (approval day, loan date or first installment
        date). Odoo applies the rate of the entry date.
        """
        self.ensure_one()
        mode = self.company_id.ent_loan_conversion_date or 'move_date'
        if mode == 'loan_date' and self.date:
            return self.date
        if mode == 'payment_date' and self.payment_date:
            return self.payment_date
        return fields.Date.context_today(self)

    def _loan_needs_conversion(self):
        """True when the loan currency differs from the company currency and
        the conversion is enabled on the company."""
        self.ensure_one()
        if not self.company_id.ent_loan_currency_conversion:
            return False
        currency = self.currency_id or self.company_id.currency_id
        return currency != self.company_id.currency_id

    def _loan_company_currency_amount(self, amount, on_date=None):
        """Convert ``amount`` (loan currency) into the company currency.

        The conversion is a setting: with ``ent_loan_currency_conversion`` off
        (or a loan already in the company currency) the amount is returned
        untouched — the legacy raw posting, which is what the switch is for.

        Uses the rate of ``on_date`` (default: the disbursement date). Without
        any rate in the database Odoo converts 1:1 — the identity is not left
        silent here: it is logged, so that a missing rate shows up instead of
        producing an entry in the wrong unit.
        """
        self.ensure_one()
        if not self._loan_needs_conversion():
            return amount
        company_currency = self.company_id.currency_id
        currency = self.currency_id or company_currency
        if currency == company_currency:
            return amount
        if on_date is None:
            on_date = self._loan_disbursement_date()
        converted = currency._convert(
            amount, company_currency, self.company_id, on_date)
        if amount and company_currency.is_zero(converted - amount):
            _logger.warning(
                "ent_loan_accounting: no %s rate found on %s — loan %s is "
                "converted 1:1 (identity). Create the currency rate so that "
                "the entry is posted in the right unit.",
                currency.display_name, on_date, self.name)
        return converted

    def _loan_carries_currency(self):
        """True when the disbursement entry can *carry* the loan currency.

        Odoo gives the journal currency precedence over the document currency:
        a CDF loan disbursed through a journal whose currency is USD cannot
        carry CDF on its entry. The amount is converted anyway (the unit stays
        right) and the situation is reported, because the amount is then not
        traceable in the loan currency.
        """
        self.ensure_one()
        if not self._loan_needs_conversion():
            return False
        journal_currency = self.journal_id.currency_id
        if journal_currency and journal_currency != self.currency_id:
            _logger.warning(
                "ent_loan_accounting: journal %s is in %s and cannot carry the "
                "%s loan %s — the disbursement is converted to the company "
                "currency without carrying the loan currency. Use a journal of "
                "the loan currency to keep the amount traceable in %s.",
                self.journal_id.display_name, journal_currency.display_name,
                self.currency_id.display_name, self.name,
                self.currency_id.display_name)
            return False
        return True

    @api.model
    def _loans_with_unconverted_disbursement(self):
        """Loans whose posted disbursement entry is not expressed in the loan
        currency — a read-only trace for ``migrations/1.0.8/post-migrate.py``.

        The module fixes the entries it creates from now on; it never reposts
        an entry that is already posted (correcting history is an accounting
        decision, not a technical one).
        """
        reported = self.browse()
        for loan in self.search([('move_id', '!=', False)]):
            if not loan._loan_needs_conversion():
                continue
            if loan.move_id.currency_id != loan.currency_id:
                reported |= loan
        return reported

    # ------------------------------------------------------------------
    # Label (reference) of the recovery entry of an installment
    # ------------------------------------------------------------------
    # The NUMBER of an accounting entry belongs to its journal. The recovery
    # route (``hr.loan.line.action_paid_amount``) used to force it
    # ('LOAN/ <employee>/<month>'), which on Odoo 18 has two consequences:
    #
    # 1. the entry is REFUSED as soon as a group of digits of the label does
    #    not match the entry date — account.sequence_mixin reads a name as a
    #    *sequence* (measured on SPORTS EXPERTS, journal BNK1:
    #    'LOAN/ DIAG W17 lot F (a supprimer)/...' — the '17' of W17 read as a
    #    year, so the entry dated 10/09/2026 was rejected by
    #    _constrains_date_sequence);
    # 2. the journal ADOPTS the label as its numbering TEMPLATE: Odoo never
    #    renumbers an entry that carries a name (account.move._compute_name),
    #    and the following entry of the journal is then born from the loan
    #    label instead of the journal sequence (same defect, same family, as
    #    the one fixed on ``ent_ohrms_salary_advance``).
    #
    # The human label therefore lives in ``ref`` — and on the entry lines —
    # and follows a *configurable* template, so the wording is a setting and
    # not a new module version:
    #
    #   ir.config_parameter : ent_loan_accounting.recovery_move_ref_template
    #   placeholders        : {reference} {employee} {period} {company}
    #   default             : 'Loan {reference} for {employee} - {period}'
    RECOVERY_REF_TEMPLATE_PARAM = 'ent_loan_accounting.recovery_move_ref_template'
    RECOVERY_REF_TEMPLATE_DEFAULT = 'Loan {reference} for {employee} - {period}'

    def _loan_recovery_move_ref(self, period=None, employee_name=None):
        """Build the reference (label) of an installment recovery entry.

        A broken template falls back on the default instead of blocking a
        payroll operation; an empty ``period`` never leaves a dangling
        separator.
        """
        self.ensure_one()
        template = self.env['ir.config_parameter'].sudo().get_param(
            self.RECOVERY_REF_TEMPLATE_PARAM) or self.RECOVERY_REF_TEMPLATE_DEFAULT
        values = {
            'reference': self.name or '',
            'employee': employee_name or self.employee_id.name or '',
            'period': period or '',
            'company': self.company_id.name or '',
        }
        try:
            ref = template.format(**values)
        except (KeyError, IndexError, ValueError):
            ref = self.RECOVERY_REF_TEMPLATE_DEFAULT.format(**values)
        ref = ref.strip()
        if not values['period']:
            ref = ref.rstrip(' -').strip()
        return ref

    def _loan_approve_vals(self, loan):
        """ Build the disbursement ('octroi') move values for one loan.

        Correct direction: **debit the loan receivable (the employee owes the
        company), credit the treasury (the money left the bank)**. The vendor
        release debited the treasury and credited the payroll payable, which
        inflated the treasury and overstated the salary due.

        Unit: when the loan is expressed in a currency other than the company
        currency, the two legs are converted at the rate of the disbursement
        date and the entry carries the loan currency (``currency_id`` +
        ``amount_currency``) so that the amount stays traceable in the loan
        currency, exactly like the payslip entry that recovers the
        installments.
        """
        loan.ensure_one()
        move_date = loan._loan_disbursement_date()
        amount = loan.loan_amount
        company_amount = loan._loan_company_currency_amount(amount, move_date)
        carries_currency = loan._loan_carries_currency()
        line_name = 'Loan ' + loan.name + ' ' + loan.employee_id.name
        move_ref = 'Loan' + ' ' + loan.name + ' for ' + loan.employee_id.name
        partner_id = loan.employee_id.work_contact_id.id or False

        def _line_vals(account_id, debit, credit, amount_currency, partner):
            vals = {
                'name': line_name,
                'account_id': account_id,
                'journal_id': loan.journal_id.id,
                'date': move_date,
                'debit': debit,
                'credit': credit,
                'loan_id': loan.id,
            }
            if partner:
                vals['partner_id'] = partner
            if carries_currency:
                vals['currency_id'] = loan.currency_id.id
                vals['amount_currency'] = amount_currency
            return vals

        debit_vals = _line_vals(
            loan.loan_account_id.id,
            company_amount > 0.0 and company_amount or 0.0,
            company_amount < 0.0 and -company_amount or 0.0,
            amount, partner_id)
        credit_vals = _line_vals(
            loan.treasury_account_id.id,
            company_amount < 0.0 and -company_amount or 0.0,
            company_amount > 0.0 and company_amount or 0.0,
            -amount, False)
        vals = {
            'ref': move_ref,
            'narration': loan.employee_id.name,
            'journal_id': loan.journal_id.id,
            'date': move_date,
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
        }
        if carries_currency:
            vals['currency_id'] = loan.currency_id.id
        return vals

    def action_approve(self):
        """ This creates an invoice in account.move with loan request details.
        """
        loan_approve = self.env['ir.config_parameter'].sudo().get_param(
            'ent_loan_accounting.loan_approve')
        contract_obj = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id)])
        if not contract_obj:
            raise UserError('You must Define a contract for employee')
        if not self.loan_line_ids:
            raise UserError('You must compute installment before Approved')
        if loan_approve:
            self.write({'state': 'waiting_approval_2'})
        else:
            self._check_loan_accounts()
            if not self.loan_line_ids:
                raise UserError(
                    'You must compute Loan Request before Approved')
            for loan in self:
                vals = loan._loan_approve_vals(loan)
                move = self.env['account.move'].create(vals)
                move.action_post()
                loan.move_id = move.id
            self.write({'state': 'approve'})
        return True

    def action_reset_to_draft(self):
        """ Reset loan to draft state and unpost related account move.
        """
        for loan in self:
            if loan.move_id:
                if loan.move_id.state == 'posted':
                    loan.move_id.button_draft()
                loan.move_id.unlink()
                loan.move_id = False
        self.write({'state': 'draft'})
        return True

    def action_double_approve(self):
        """ This creates account move for request in case of double approval.
        """
        self._check_loan_accounts()
        if not self.loan_line_ids:
            raise UserError('You must compute Loan Request before Approved')
        for loan in self:
            vals = loan._loan_approve_vals(loan)
            move = self.env['account.move'].create(vals)
            move.action_post()
            loan.move_id = move.id
        self.write({'state': 'approve'})
        return True
