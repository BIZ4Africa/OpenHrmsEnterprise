# -*- coding: utf-8 -*-
"""Non-regression guard on the NAME of the recovery entry of an installment.

Defect measured on the SPORTS EXPERTS instance (2026-10-09, card t_c6e17a81,
section 6a of the lot F report): ``hr.loan.line.action_paid_amount()`` forced the
name of the accounting entry it creates — ``'LOAN/' + ' ' + employee + '/' + month``.
Two consequences, both on Odoo 18:

1. **The entry is rejected.** ``account.models.sequence_mixin`` reads a name as a
   *sequence*: any group of digits in the label can be parsed as a year or a
   month, and ``_constrains_date_sequence`` then requires it to match the entry
   date. Measured label: ``'LOAN/ DIAG W17 lot F (a supprimer)/DIAG-lot-F'`` —
   the ``17`` of ``W17`` was read as the year, so the entry dated 10/09/2026 was
   refused::

       ValidationError: The Date (10/09/2026) you've entered isn't aligned with
       the existing sequence number (LOAN/ DIAG W17 lot F (a supprimer)/...).

2. **The journal numbering is hijacked.** Odoo never renumbers an entry that
   already carries a name (``account.move._compute_name``), and
   ``sequence.mixin._get_last_sequence`` then adopts that free name as the
   numbering *template* of the journal: the next entry of the journal is born
   from the loan label instead of the journal sequence (the same defect, same
   family, measured on ``ent_ohrms_salary_advance``; commit 286cc87).

The entry number belongs to the journal (``BNK1/2026/00005``); the human label
belongs to ``ref`` and to the entry lines. The tests below fail whenever the
module forces a free name again, when the entry is not postable on a **bank**
journal, or when the label stops following its configurable template.
"""
from datetime import date

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

REF_TEMPLATE_PARAM = 'ent_loan_accounting.recovery_move_ref_template'
REF_TEMPLATE_DEFAULT = 'Loan {reference} for {employee} - {period}'


@tagged('post_install', '-at_install')
class TestLoanRecoveryMoveName(TransactionCase):
    """Name of the entry produced by the recovery of an installment."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company_currency = cls.company.currency_id
        # The employee label of the measured failure: 'W17' is the token the
        # account sequence mixin read as a year ('17' != 2026).
        cls.employee = cls.env['hr.employee'].create({
            'name': 'DIAG W17 lot F (a supprimer)',
        })
        cls.env['hr.contract'].create({
            'name': 'Loan Recovery Name Test Contract',
            'employee_id': cls.employee.id,
            'date_start': date(2024, 1, 1),
            'wage': 100000.0,
        })

    def setUp(self):
        super().setUp()
        self.receivable = self._account(
            '421100', 'Personnel, avances', 'asset_receivable')
        self.payroll_payable = self._account(
            '422000', 'Personnel, remunerations dues', 'liability_payable')
        self.treasury = self._account('521001', 'Banque', 'asset_cash')
        # A BANK journal: the measured failure, and the case of the client
        # instance (BNK1). Its own numbering is 'LRTB/<year>/<00000>'.
        self.journal = self.env['account.journal'].create({
            'name': 'Loan Recovery Name Test Journal',
            'code': 'LRTB',
            'type': 'bank',
        })
        self.assertIn('bank', (self.journal.type,),
                      "the regression must be measured on a bank journal")

    # ------------------------------------------------------------------ outils
    def _account(self, code, name, account_type):
        account = self.env['account.account'].search(
            [('code', '=', code)], limit=1)
        if not account:
            account = self.env['account.account'].create({
                'code': code, 'name': name, 'account_type': account_type,
            })
        return account

    def _make_loan(self, employee=None):
        loan = self.env['hr.loan'].create({
            'employee_id': (employee or self.employee).id,
            'loan_amount': 300000.0,
            'currency_id': self.company_currency.id,
            'installment': 3,
            'payment_date': date(2026, 1, 31),
            'treasury_account_id': self.treasury.id,
            'employee_account_id': self.payroll_payable.id,
            'loan_account_id': self.receivable.id,
            'journal_id': self.journal.id,
        })
        loan.action_compute_installment()
        loan.action_approve()
        return loan

    def _recovery_moves(self, loan):
        return self.env['account.move'].search([
            ('journal_id', '=', self.journal.id),
            ('id', '!=', loan.move_id.id),
        ], order='id')

    # ------------------------------------------------- the measured failure
    def test_installment_payment_posts_on_a_bank_journal(self):
        """A payment must post — today it is refused by the date/sequence rule.

        Reproduces ``tools/m86_diag_paid.out`` / ``tools/m87_probe_labels.out``
        of card t_c6e17a81: the label of the measured failure (employee ``W17``,
        period ``Octobre-2026``) on a bank journal.
        """
        loan = self._make_loan()
        installment = loan.loan_line_ids[:1]
        self.assertTrue(installment, "the loan must have installments")
        installment.action_paid_amount('Octobre-2026')  # must not raise

        moves = self._recovery_moves(loan)
        self.assertEqual(len(moves), 1,
                         "the payment must have posted one entry, found %s"
                         % len(moves))
        self.assertEqual(moves.state, 'posted')

    def test_entry_number_is_the_journal_numbering(self):
        """The number of the entry is the journal's, not a free 'LOAN/ ...'."""
        loan = self._make_loan()
        loan.loan_line_ids[0].action_paid_amount('Octobre-2026')
        move = self._recovery_moves(loan)
        self.assertTrue(
            move.name.startswith(self.journal.code + '/'),
            'entry name %r is not the journal numbering (%s/*)'
            % (move.name, self.journal.code))
        self.assertNotIn('LOAN', move.name or '',
                         "no free name may be forced on the entry")

    def test_the_journal_numbering_is_not_hijacked(self):
        """A following entry of the journal keeps the journal numbering.

        Odoo never renumbers an entry that already has a name, and the journal
        adopts that name as its numbering template: with a forced name the next
        entry of the journal is born from the loan label. A label without any
        digit is used here, so that the entry posts (the date/sequence rule of
        the first test does not fire) and the hijacking is measured on its own.
        """
        employee = self.env['hr.employee'].create(
            {'name': 'Recovery Hijack Employee'})
        self.env['hr.contract'].create({
            'name': 'Recovery Hijack Contract',
            'employee_id': employee.id,
            'date_start': date(2024, 1, 1),
            'wage': 100000.0,
        })
        loan = self._make_loan(employee)
        loan.loan_line_ids[0].action_paid_amount('premiere-tranche')
        partner = employee.work_contact_id
        following = self.env['account.move'].create({
            'journal_id': self.journal.id,
            'date': date(2026, 10, 15),
            'line_ids': [
                (0, 0, {'name': 'probe', 'partner_id': partner.id,
                        'account_id': self.receivable.id,
                        'debit': 10.0, 'credit': 0.0}),
                (0, 0, {'name': 'probe', 'partner_id': partner.id,
                        'account_id': self.treasury.id,
                        'debit': 0.0, 'credit': 10.0}),
            ],
        })
        following.action_post()
        self.assertTrue(
            following.name.startswith(self.journal.code + '/'),
            'the entry following a loan installment is named %r — the loan '
            'label has been adopted as the journal numbering template'
            % following.name)
        self.assertNotIn('LOAN', following.name or '')

    # ------------------------------------------------------------- the label
    def test_the_label_lives_on_the_lines_and_in_ref(self):
        """The human label is on the entry lines and in ``ref``."""
        loan = self._make_loan()
        loan.loan_line_ids[0].action_paid_amount('Octobre-2026')
        move = self._recovery_moves(loan)

        self.assertEqual(
            move.ref, REF_TEMPLATE_DEFAULT.format(
                reference=loan.name, employee=self.employee.name,
                period='Octobre-2026'))
        for line in move.line_ids:
            self.assertIn(self.employee.name, line.name or '',
                          "the employee must stay readable on the entry lines")
            self.assertIn('Octobre-2026', line.name or '',
                          "the period must stay readable on the entry lines")

    def test_the_label_template_is_configurable(self):
        """The wording of the label is a setting, not a constant."""
        self.env['ir.config_parameter'].sudo().set_param(
            REF_TEMPLATE_PARAM,
            'Recuperation {period} du pret {reference} — {employee}')
        loan = self._make_loan()
        loan.loan_line_ids[0].action_paid_amount('Octobre-2026')
        move = self._recovery_moves(loan)
        self.assertEqual(
            move.ref,
            'Recuperation Octobre-2026 du pret %s — %s'
            % (loan.name, self.employee.name))

    def test_a_broken_template_falls_back_on_the_default(self):
        """A broken template must never block a payroll operation."""
        self.env['ir.config_parameter'].sudo().set_param(
            REF_TEMPLATE_PARAM, 'Recuperation {unknown_placeholder}')
        loan = self._make_loan()
        loan.loan_line_ids[0].action_paid_amount('Octobre-2026')
        move = self._recovery_moves(loan)
        self.assertEqual(
            move.ref, REF_TEMPLATE_DEFAULT.format(
                reference=loan.name, employee=self.employee.name,
                period='Octobre-2026'))

    def test_no_period_leaves_no_dangling_separator(self):
        """Calling the recovery without a period stays readable."""
        loan = self._make_loan()
        loan.loan_line_ids[0].action_paid_amount(None)
        move = self._recovery_moves(loan)
        self.assertFalse(move.ref.endswith('-'),
                         "the label %r ends on a dangling separator"
                         % move.ref)
        self.assertIn(self.employee.name, move.ref)
