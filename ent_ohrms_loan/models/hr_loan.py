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
import logging

from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrLoan(models.Model):
    """Model for Loan Requests for employees."""
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    # Reference series of the loans. One sequence is provisioned **per
    # company**: a reference series belongs to a single entity, so a loan of
    # company B is numbered from the series of company B.
    LOAN_SEQUENCE_CODE = 'hr.loan.seq'
    # Configuration parameter holding the prefix of the loan references. A
    # per-company override exists under '<param>_<company_id>'.
    LOAN_SEQUENCE_PREFIX_PARAM = 'ent_ohrms_loan.loan_sequence_prefix'

    name = fields.Char(string="Loan Name", default="/", readonly=True,
                       help="Name of the loan")
    date = fields.Date(string="Date", default=fields.Date.today(),
                       help="Date of the loan")
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee",
                                  required=True, help="Employee for the loan")
    department_id = fields.Many2one(comodel_name='hr.department',
                                    related="employee_id.department_id",
                                    readonly=True,
                                    string="Department",
                                    help="Department of employee")
    installment = fields.Integer(string="No Of Installments", default=1,
                                 help="Number of installments")
    payment_date = fields.Date(string="Payment Start Date", required=True,
                               default=fields.Date.today(),
                               help="Date of the payment")
    loan_line_ids = fields.One2many(comodel_name='hr.loan.line',
                                    help="Details of the Loan Repayment",
                                    inverse_name='loan_id', string="Loan Line",
                                    index=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 help="Company",
                                 default=lambda self:
                                 self.env.user.company_id if self else None)
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  string='Currency', required=True,
                                  help="Currency",
                                  default=lambda self:
                                  self.env.user.company_id.currency_id if self
                                  else None)
    job_position_id = fields.Many2one(comodel_name='hr.job',
                                      related="employee_id.job_id",
                                      readonly=True, string="Job Position",
                                      help="Job position of employee")
    loan_amount = fields.Float(string="Loan Amount", required=True,
                               help="Loan amount")
    total_amount = fields.Float(string="Total Amount", store=True,
                                readonly=True, compute='_compute_loan_amount',
                                help="Total loan amount")
    balance_amount = fields.Float(string="Balance Amount", store=True,
                                  compute='_compute_loan_amount',
                                  help="Balance amount")
    total_paid_amount = fields.Float(string="Total Paid Amount", store=True,
                                     compute='_compute_loan_amount',
                                     help="Total paid amount")
    state = fields.Selection([
        ('draft', 'Draft'), ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'), ('refuse', 'Refused'), ('cancel', 'Canceled'),
    ], string="State", help="State of loan request", default='draft',
        tracking=True, copy=False, )

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        if "employee_id" not in field_list:
            return {k: v for k, v in result.items() if k in field_list}
        employee_id = result.get("employee_id")
        if not employee_id:
            ts_user_id = result.get("user_id") or self.env.context.get(
                "user_id", self.env.user.id
            )
            result["employee_id"] = (
                self.env["hr.employee"]
                .search([("user_id", "=", ts_user_id)], limit=1)
                .id
            )
        return {k: v for k, v in result.items() if k in field_list}

    def _compute_loan_amount(self):
        """ calculate the total amount paid towards the loan. """
        for loan in self:
            total_paid = 0.0
            for line in loan.loan_line_ids:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

    # --- Loan reference sequence (one series per company) -----------------

    @api.model
    def _loan_sequence_prefix(self, company):
        """Prefix of the loan references of ``company``.

        Configurable, in order of precedence:

        * ``ent_ohrms_loan.loan_sequence_prefix_<company_id>`` — per company;
        * ``ent_ohrms_loan.loan_sequence_prefix`` — global default;
        * ``LO/`` — the historical prefix of the module.
        """
        Parameter = self.env['ir.config_parameter'].sudo()
        return (
            Parameter.get_param(
                '%s_%s' % (self.LOAN_SEQUENCE_PREFIX_PARAM, company.id))
            or Parameter.get_param(self.LOAN_SEQUENCE_PREFIX_PARAM)
            or 'LO/'
        )

    @api.model
    def _loan_sequence(self, company):
        """The loan sequence owned by ``company`` (never a shared one)."""
        return self.env['ir.sequence'].sudo().search(
            [('code', '=', self.LOAN_SEQUENCE_CODE),
             ('company_id', '=', company.id)], limit=1)

    @api.model
    def _ensure_loan_sequences(self, companies=None):
        """Guarantee one loan sequence per company, idempotently.

        A company that already owns a sequence is left untouched, so the hook
        runs at install and at every upgrade without ever creating a
        duplicate. Each sequence is explicitly bound to its company — no
        company-less (shared) series is created, and no company is left
        relying on the series of another one. Returns the created sequences.
        """
        Sequence = self.env['ir.sequence'].sudo()
        if companies is None:
            companies = self.env['res.company'].with_context(
                active_test=False).search([])
        created = Sequence.browse()
        for company in companies:
            if self._loan_sequence(company):
                continue
            sequence = Sequence.create({
                'name': 'Loan Request - %s' % company.name,
                'code': self.LOAN_SEQUENCE_CODE,
                'prefix': self._loan_sequence_prefix(company),
                'padding': 4,
                'number_increment': 1,
                'number_next_actual': 1,
                'implementation': 'standard',
                'company_id': company.id,
            })
            created |= sequence
            _logger.info(
                "ent_ohrms_loan: loan sequence %s created for company %s "
                "(prefix %r).", sequence.id, company.display_name,
                sequence.prefix)
        return created

    @api.model
    def _next_loan_sequence(self, company):
        """Draw the next loan reference of ``company``.

        The series is identified by the company of the loan, not by the
        ambient company of the user: a loan of company B takes its reference
        from the series of company B even when it is created from company A.

        A missing sequence is a configuration error: it raises a UserError on
        the creating operation -- the user sees the refusal in the interface
        and nothing is written -- and is never silently replaced by a blank
        name, that blank fallback being exactly what kept the defect invisible.

        The guard does not log: the operation is already refused, and an
        ERROR/WARNING line emitted on a path walked by the installation or the
        tests would only colour the build (N2 rule: block on the business
        operation, never mark the build).
        """
        sequence = self._loan_sequence(company)
        if not sequence:
            raise UserError(_(
                "No loan reference sequence ('%s') is configured for the "
                "company '%s'. Ask an administrator to provision the loan "
                "sequences of every company before creating a loan."
            ) % (self.LOAN_SEQUENCE_CODE, company.display_name))
        return sequence.with_company(company).next_by_id()

    @api.model
    def _backfill_empty_loan_names(self):
        """Name the loans that carry no usable reference.

        Only loans whose ``name`` is empty or the module placeholder ('/',
        ' ') are touched; each is named once, from the sequence of **its own**
        company. Idempotent (an already named loan is never renamed) and
        strictly limited to ``hr.loan.name``: no accounting entry is written,
        so the labels of entries already posted are left as they were.
        Returns the loans renamed.
        """
        renamed = self.browse()
        for loan in self.search([]):
            if (loan.name or '').strip() not in ('', '/'):
                continue
            if not loan.company_id:
                continue
            previous = loan.name
            name = self._next_loan_sequence(loan.company_id)
            loan.with_company(loan.company_id).write({'name': name})
            renamed |= loan
            _logger.info(
                "ent_ohrms_loan: loan %s (company %s) renamed from %r to %r.",
                loan.id, loan.company_id.display_name, previous, name)
        return renamed

    @api.model_create_multi
    def create(self, vals_list):
        """Creates new HR loan records with the provided values."""
        for values in vals_list:
            loan_count = self.env['hr.loan'].search_count(
                [('employee_id', '=', values['employee_id']),
                 ('state', '=', 'approve'),
                 ('balance_amount', '!=', 0)])
            if loan_count:
                raise ValidationError(
                    _("The employee has already a pending installment"))
            company = self.env['res.company'].browse(
                values.get('company_id')
                or self.env.context.get('default_company_id')
                or self.env.company.id)
            # A reference already supplied by the caller (a dependent module
            # for instance) is kept as is; only the module placeholder ('/',
            # ' ' or empty) is replaced, from the sequence of the loan's own
            # company. A missing sequence raises -- never a blank fallback.
            # NOTE: `ir.sequence.get()` does not exist in 19.0 (removed after
            # 18.0); the reference is drawn from the sequence of the loan's
            # own company.
            if not values.get('name') or values.get('name') in ('/', ' '):
                values['name'] = self._next_loan_sequence(company)
        return super().create(vals_list)

    def action_compute_installment(self):
        """This automatically create the installment the employee need to pay
        to company based on payment start date and the no of installments."""
        for loan in self:
            loan.loan_line_ids.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
            loan._compute_loan_amount()
        return True

    def action_refuse(self):
        """Action to refuse the loan"""
        return self.write({'state': 'refuse'})

    def action_submit(self):
        """Action to submit the loan"""
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        """Action to cancel the loan"""
        self.write({'state': 'cancel'})

    def action_approve(self):
        """Approve loan by the manager"""
        for data in self:
            if not data.loan_line_ids:
                raise ValidationError(_("Please Compute installment"))
            else:
                self.write({'state': 'approve'})

    def unlink(self):
        """Unlink loan lines"""
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or '
                    'cancelled state')
        return super().unlink()
