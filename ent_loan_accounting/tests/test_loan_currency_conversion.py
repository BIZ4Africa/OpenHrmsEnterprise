# -*- coding: utf-8 -*-
"""Non-regression guard on the ACCOUNTING UNIT of the loan disbursement.

Defect measured on the SPORTS EXPERTS instance (2026-10-09, card t_c6e17a81),
module ``ent_loan_accounting`` 1.0.7: the disbursement ('octroi') of a loan
expressed in a currency other than the company currency was posted **raw** in
the company currency — ``ent_loan_accounting`` never read
``hr.loan.currency_id``. On company 2 (USD books, 2 265 CDF/USD) the entry was
``D 421100 300 000 / C 521001 300 000`` USD for a 300 000 CDF loan (132,45 USD)
while the payslip recovery — which does convert — posted 44,15 USD per
installment: 299 867,55 USD of the receivable could never be settled.

Asserted here:

* a foreign-currency loan produces a disbursement entry **converted** at the
  rate of the entry date, carrying the loan currency (``currency_id`` +
  ``amount_currency``);
* the three installments, converted the same way, bring the receivable back to
  exactly zero;
* the conversion is a **configuration** (switch + entry date), not a constant;
* a loan in the company currency keeps the legacy posting;
* the pre-1.0.8 trace reports the unconverted entries without reposting them.

The first test fails if an amount is posted without conversion.
"""
import os
from datetime import date

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestLoanDisbursementCurrency(TransactionCase):
    """Accounting unit of the disbursement and of the recovery."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company_currency = cls.company.currency_id
        cls.rate = 2265.0  # same shape as the CDF rate of the client instance
        cls.foreign = cls.env['res.currency'].create({
            'name': 'TST',
            'symbol': 'T',
            'rounding': 0.01,
        })
        cls.env['res.currency.rate'].create({
            'currency_id': cls.foreign.id,
            'name': date(2025, 1, 1),
            'rate': cls.rate,
            'company_id': cls.company.id,
        })
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Loan Currency Test Employee',
        })
        cls.env['hr.contract'].create({
            'name': 'Loan Currency Test Contract',
            'employee_id': cls.employee.id,
            'date_start': date(2024, 1, 1),
            'wage': 100000.0,
        })

    # ------------------------------------------------------------------ outils
    def _account(self, code, name, account_type):
        account = self.env['account.account'].search(
            [('code', '=', code)], limit=1)
        if not account:
            account = self.env['account.account'].create({
                'code': code, 'name': name, 'account_type': account_type,
            })
        return account

    def _make_loan(self, amount, currency=None, employee=None):
        employee = employee or self.env['hr.employee'].create({
            'name': 'Loan Currency Test Employee %s' % amount,
        })
        self.env['hr.contract'].create({
            'name': 'Contract %s' % employee.name,
            'employee_id': employee.id,
            'date_start': date(2024, 1, 1),
            'wage': 100000.0,
        })
        loan = self.env['hr.loan'].create({
            'employee_id': employee.id,
            'loan_amount': amount,
            'currency_id': (currency or self.company_currency).id,
            'installment': 3,
            'payment_date': date(2026, 1, 31),
            'treasury_account_id': self.treasury.id,
            'employee_account_id': self.payroll_payable.id,
            'loan_account_id': self.receivable.id,
            'journal_id': self.journal.id,
        })
        loan.action_compute_installment()
        return loan

    def setUp(self):
        super().setUp()
        self.receivable = self._account(
            '421100', 'Personnel, avances', 'asset_receivable')
        self.payroll_payable = self._account(
            '422000', 'Personnel, remunerations dues', 'liability_payable')
        self.treasury = self._account('521001', 'Banque', 'asset_cash')
        self.journal = self.env['account.journal'].create({
            'name': 'Loan Currency Test Journal',
            'code': 'LCTJ',
            'type': 'general',
        })

    def _lines_by_account(self, move):
        return {line.account_id: line for line in move.line_ids}

    # ------------------------------------------------------------- conversion
    def test_disbursement_of_a_foreign_loan_is_converted(self):
        """300 000 TST @ 2 265 = 132,45 company currency — never 300 000."""
        loan = self._make_loan(300000.0, currency=self.foreign)
        loan.action_approve()
        move = loan.move_id
        self.assertTrue(move, "the approval must post a disbursement entry")
        self.assertEqual(move.state, 'posted')

        # the entry carries the loan currency (traceability in the loan unit)
        self.assertEqual(move.currency_id, self.foreign)
        lines = self._lines_by_account(move)
        converted = round(300000.0 / self.rate, 2)

        receivable = lines[self.receivable]
        treasury = lines[self.treasury]
        self.assertAlmostEqual(receivable.debit, converted, places=2)
        self.assertAlmostEqual(receivable.credit, 0.0, places=2)
        self.assertAlmostEqual(treasury.credit, converted, places=2)
        self.assertAlmostEqual(treasury.debit, 0.0, places=2)
        self.assertAlmostEqual(receivable.amount_currency, 300000.0, places=2)
        self.assertAlmostEqual(treasury.amount_currency, -300000.0, places=2)

        # the exact defect of 1.0.7: the raw amount, posted unconverted
        self.assertNotAlmostEqual(
            receivable.debit, 300000.0, places=2,
            msg="the disbursement must not be posted in the raw loan amount")
        self.assertAlmostEqual(
            sum(move.line_ids.mapped('debit')),
            sum(move.line_ids.mapped('credit')), places=2,
            msg="the disbursement entry must be balanced")

    def test_installments_converted_settle_the_receivable(self):
        """3 × 100 000 TST @ 2 265 = 3 × 44,15 = 132,45 -> receivable at zero."""
        loan = self._make_loan(300000.0, currency=self.foreign)
        loan.action_approve()
        # this legacy route forces the move name ('LOAN/ <employee>/<label>'),
        # unique per journal, and the label must not look like a numeric month:
        # the account sequence mixin would otherwise check it against the entry
        # date. One label per installment, nothing else is asserted here.
        labels = ['premiere-tranche', 'deuxieme-tranche', 'troisieme-tranche']
        for installment, label in zip(loan.loan_line_ids, labels):
            installment.action_paid_amount(label)
        moves = self.env['account.move'].search([('ref', '=', loan.name)])
        recovered = sum(
            sum(move.line_ids.filtered(
                lambda line: line.account_id == self.receivable and line.credit
            ).mapped('credit'))
            for move in moves)

        self.assertAlmostEqual(recovered, 132.45, places=2)
        balance = sum(self.env['account.move.line'].search([
            ('account_id', '=', self.receivable.id),
            ('move_id', 'in', moves.ids + loan.move_id.ids),
        ]).mapped('balance'))
        self.assertAlmostEqual(
            balance, 0.0, places=2,
            msg="the converted installments must settle the converted "
                "disbursement exactly")

    def test_same_currency_loan_keeps_the_legacy_posting(self):
        """A loan in the company currency is not converted at all."""
        loan = self._make_loan(300000.0)
        loan.action_approve()
        move = loan.move_id
        self.assertEqual(move.currency_id, self.company_currency)
        lines = self._lines_by_account(move)
        self.assertAlmostEqual(lines[self.receivable].debit, 300000.0, places=2)
        self.assertAlmostEqual(lines[self.treasury].credit, 300000.0, places=2)

    # --------------------------------------------------------- parametrisation
    def test_switch_disables_the_conversion(self):
        """The behaviour is a setting: off -> legacy raw posting."""
        self.company.ent_loan_currency_conversion = False
        loan = self._make_loan(300000.0, currency=self.foreign)
        self.assertFalse(loan._loan_needs_conversion())
        loan.action_approve()
        move = loan.move_id
        self.assertEqual(move.currency_id, self.company_currency)
        lines = self._lines_by_account(move)
        self.assertAlmostEqual(lines[self.receivable].debit, 300000.0, places=2)
        self.assertAlmostEqual(lines[self.treasury].credit, 300000.0, places=2)

    def test_recovery_conversion_follows_the_company_switch(self):
        """The installment entry obeys the same setting as the disbursement."""
        self.company.ent_loan_currency_conversion = False
        loan = self._make_loan(300000.0, currency=self.foreign)
        loan.action_approve()
        installment = loan.loan_line_ids[:1]
        installment.action_paid_amount('October-2026')
        move = self.env['account.move'].search([('ref', '=', loan.name)])
        lines = self._lines_by_account(move)
        self.assertAlmostEqual(lines[self.payroll_payable].debit, 100000.0,
                               places=2)
        self.assertAlmostEqual(lines[self.receivable].credit, 100000.0,
                               places=2)

    def test_conversion_date_is_configurable(self):
        """The rate applied is the rate of the configured entry date."""
        self.foreign.rate_ids.unlink()
        self.env['res.currency.rate'].create({
            'currency_id': self.foreign.id,
            'name': date(2025, 1, 1),
            'rate': 2265.0,
            'company_id': self.company.id,
        })
        self.env['res.currency.rate'].create({
            'currency_id': self.foreign.id,
            'name': date(2027, 1, 1),
            'rate': 1000.0,
            'company_id': self.company.id,
        })
        # default: accounting entry date (today) -> rate 2 265
        by_move_date = self._make_loan(300000.0, currency=self.foreign)
        by_move_date.action_approve()
        self.assertAlmostEqual(
            self._lines_by_account(by_move_date.move_id)[self.receivable].debit,
            132.45, places=2)

        # configured on the loan date (2027) -> rate 1 000
        self.company.ent_loan_conversion_date = 'loan_date'
        on_loan_date = self._make_loan(300000.0, currency=self.foreign)
        on_loan_date.date = date(2027, 6, 15)
        on_loan_date.action_approve()
        move = on_loan_date.move_id
        self.assertEqual(move.date, date(2027, 6, 15))
        self.assertAlmostEqual(
            self._lines_by_account(move)[self.receivable].debit, 300.0,
            places=2)

    def test_missing_rate_is_reported_not_silent(self):
        """A currency without any rate converts 1:1 — and says so."""
        orphan = self.env['res.currency'].create({
            'name': 'ORP', 'symbol': 'O', 'rounding': 0.01,
        })
        loan = self._make_loan(50000.0, currency=orphan)
        with self.assertLogs(
                'odoo.addons.ent_loan_accounting.models.hr_loan',
                level='WARNING') as logs:
            loan.action_approve()
        self.assertTrue(
            any('1:1' in message for message in logs.output),
            "a conversion without any rate must be reported: %s" % logs.output)

    # ------------------------------------------------------------------ trace
    def test_migration_switches_the_conversion_on(self):
        """The 1.0.8 migration really enables the switch on existing companies.

        Odoo adds a Boolean column with ``DEFAULT false`` and only backfills
        the rows that are still NULL, so the field ``default=True`` never
        reaches a company that already exists: without this hook the fix would
        ship and stay inert on the client instance.
        """
        from importlib.util import module_from_spec, spec_from_file_location
        from odoo.modules.module import get_module_path

        path = os.path.join(
            get_module_path('ent_loan_accounting'),
            'migrations', '1.0.8', 'post-migrate.py')
        spec = spec_from_file_location('ent_loan_accounting_mig_108', path)
        migration = module_from_spec(spec)
        spec.loader.exec_module(migration)

        self.company.ent_loan_currency_conversion = False
        changed = migration.activate_currency_conversion(self.env)
        self.assertIn(self.company, changed)
        self.assertTrue(self.company.ent_loan_currency_conversion,
                        "the migration must enable the conversion on an "
                        "existing company")

    def test_unconverted_disbursement_trace_is_read_only(self):
        """The 1.0.8 migration reports the legacy entries, it never reposts."""
        self.company.ent_loan_currency_conversion = False
        loan = self._make_loan(300000.0, currency=self.foreign)
        loan.action_approve()
        move = loan.move_id
        self.company.ent_loan_currency_conversion = True

        before = (move.currency_id, move.state, move.name,
                  move.line_ids.mapped('debit'), move.line_ids.mapped('credit'))
        moves_before = self.env['account.move'].search_count([])
        reported = self.env['hr.loan']._loans_with_unconverted_disbursement()
        after = (move.currency_id, move.state, move.name,
                 move.line_ids.mapped('debit'), move.line_ids.mapped('credit'))

        self.assertIn(loan, reported)
        self.assertEqual(before, after,
                         "the trace must not touch the posted entry")
        self.assertEqual(self.env['account.move'].search_count([]),
                         moves_before,
                         "the trace must not post anything")
