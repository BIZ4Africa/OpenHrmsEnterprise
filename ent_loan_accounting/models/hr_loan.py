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
from odoo import fields, models
from odoo.exceptions import UserError


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

    def _loan_approve_vals(self, loan):
        """ Build the disbursement ('octroi') move values for one loan.

        Correct direction: **debit the loan receivable (the employee owes the
        company), credit the treasury (the money left the bank)**. The vendor
        release debited the treasury and credited the payroll payable, which
        inflated the treasury and overstated the salary due.
        """
        line_name = 'Loan ' + loan.name + ' ' + loan.employee_id.name
        move_ref = 'Loan' + ' ' + loan.name + ' for ' + loan.employee_id.name
        partner_id = loan.employee_id.work_contact_id.id or False
        debit_vals = {
            'name': line_name,
            'account_id': loan.loan_account_id.id,
            'journal_id': loan.journal_id.id,
            'date': date.today(),
            'debit': loan.loan_amount > 0.0 and loan.loan_amount or 0.0,
            'credit': loan.loan_amount < 0.0 and -loan.loan_amount or 0.0,
            'loan_id': loan.id,
            'partner_id': partner_id,
        }
        credit_vals = {
            'name': line_name,
            'account_id': loan.treasury_account_id.id,
            'journal_id': loan.journal_id.id,
            'date': date.today(),
            'debit': loan.loan_amount < 0.0 and -loan.loan_amount or 0.0,
            'credit': loan.loan_amount > 0.0 and loan.loan_amount or 0.0,
            'loan_id': loan.id,
        }
        return {
            'ref': move_ref,
            'narration': loan.employee_id.name,
            'journal_id': loan.journal_id.id,
            'date': date.today(),
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
        }

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
