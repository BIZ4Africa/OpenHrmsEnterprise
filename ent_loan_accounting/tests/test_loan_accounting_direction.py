# -*- coding: utf-8 -*-
"""Non-regression guard on the DIRECTION of the two employee-loan legs.

Defect measured on the SPORTS EXPERTS instance (W15, 2026-10-08), module
``ent_loan_accounting`` 1.0.6: the disbursement ('octroi') move was posted
``D treasury / C payroll payable`` — the bank was debited (treasury inflated by
the loan amount) and the salary due to the employee was credited. The recovery
('récupération') move credited the treasury a second time.

Correct direction, asserted here:

* disbursement: ``D loan receivable / C treasury``
* recovery (payslip installment): ``D payroll payable / C loan receivable``

The test fails if the direction flips back.
"""
from datetime import date

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestLoanAccountingDirection(TransactionCase):
    """Direction of the loan disbursement and of the first recovery."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.loan_account = cls._get_or_create_account(
            '421100', 'Personnel, avances', 'asset_receivable')
        cls.employee_account = cls._get_or_create_account(
            '422000', 'Personnel, remunerations dues', 'liability_payable')
        cls.treasury_account = cls._get_or_create_account(
            '521001', 'Banque', 'asset_cash')
        cls.journal = cls.env['account.journal'].create({
            'name': 'Loan Direction Test Journal',
            'code': 'LDTJ',
            'type': 'general',
        })
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Loan Direction Test Employee',
        })
        cls.env['hr.contract'].create({
            'name': 'Loan Direction Test Contract',
            'employee_id': cls.employee.id,
            'date_start': date(2024, 1, 1),
            'wage': 100000.0,
        })

    @classmethod
    def _get_or_create_account(cls, code, name, account_type):
        account = cls.env['account.account'].search(
            [('code', '=', code)], limit=1)
        if not account:
            account = cls.env['account.account'].create({
                'code': code,
                'name': name,
                'account_type': account_type,
            })
        return account

    def setUp(self):
        super().setUp()
        self.loan = self.env['hr.loan'].create({
            'employee_id': self.employee.id,
            'loan_amount': 300000.0,
            'installment': 3,
            'payment_date': date(2026, 1, 31),
            'treasury_account_id': self.treasury_account.id,
            'employee_account_id': self.employee_account.id,
            'loan_account_id': self.loan_account.id,
            'journal_id': self.journal.id,
        })
        self.loan.action_compute_installment()

    def _lines_by_account(self, move):
        return {line.account_id: line for line in move.line_ids}

    # ---------------------------------------------------------------- octroi
    def test_disbursement_debits_loan_and_credits_treasury(self):
        """D loan receivable / C treasury — never the reverse."""
        self.loan.action_approve()
        move = self.loan.move_id
        self.assertTrue(move, "the approval must post a disbursement move")
        self.assertEqual(move.state, 'posted')
        self.assertAlmostEqual(
            sum(move.line_ids.mapped('debit')),
            sum(move.line_ids.mapped('credit')),
            msg="the disbursement entry must be balanced")

        lines = self._lines_by_account(move)
        self.assertIn(self.loan_account, lines,
                      "the loan receivable must carry the disbursement")
        self.assertIn(self.treasury_account, lines,
                      "the treasury must carry the disbursement")
        self.assertNotIn(
            self.employee_account, lines,
            "the payroll payable must NOT be touched at disbursement")

        self.assertAlmostEqual(lines[self.loan_account].debit, 300000.0)
        self.assertAlmostEqual(lines[self.loan_account].credit, 0.0)
        self.assertAlmostEqual(lines[self.treasury_account].credit, 300000.0)
        # the exact defect of 1.0.6: the treasury was debited
        self.assertAlmostEqual(
            lines[self.treasury_account].debit, 0.0,
            msg="the treasury must never be debited by a loan disbursement")

    def test_disbursement_refuses_without_loan_account(self):
        """A loan without a receivable account cannot produce an entry."""
        self.loan.loan_account_id = False
        with self.assertRaises(Exception):
            self.loan.action_approve()

    # ------------------------------------------------------------ recuperation
    def test_recovery_debits_payroll_and_credits_loan(self):
        """D payroll payable / C loan receivable — the treasury is untouched."""
        self.loan.action_approve()
        self.env.cr.flush()
        installment = self.loan.loan_line_ids[:1]
        self.assertAlmostEqual(installment.amount, 100000.0)

        recovery = self.env['account.move'].search([
            ('ref', '=', self.loan.name),
        ])
        self.assertFalse(recovery, "no recovery entry exists yet")

        installment.action_paid_amount('January-2026')

        recovery = self.env['account.move'].search([
            ('ref', '=', self.loan.name),
        ])
        self.assertEqual(len(recovery), 1,
                         "the recovery must post exactly one entry")
        self.assertEqual(recovery.state, 'posted')
        self.assertAlmostEqual(
            sum(recovery.line_ids.mapped('debit')),
            sum(recovery.line_ids.mapped('credit')))

        lines = self._lines_by_account(recovery)
        self.assertIn(self.employee_account, lines,
                      "the payroll payable must be debited by the recovery")
        self.assertIn(self.loan_account, lines,
                      "the loan receivable must be credited by the recovery")
        self.assertNotIn(
            self.treasury_account, lines,
            "the treasury must NOT be touched by a payslip recovery")

        self.assertAlmostEqual(lines[self.employee_account].debit, 100000.0)
        self.assertAlmostEqual(lines[self.employee_account].credit, 0.0)
        self.assertAlmostEqual(lines[self.loan_account].credit, 100000.0)
        self.assertAlmostEqual(lines[self.loan_account].debit, 0.0)

    # ----------------------------------------------------------------- arming
    def test_arm_loan_recovery_is_idempotent(self):
        """A structure without the LO rule can be armed, once."""
        Structure = self.env['hr.payroll.structure']
        Rule = self.env['hr.salary.rule']
        template = Rule.search([('code', '=', 'LO')], limit=1)
        self.assertTrue(template,
                        "ent_ohrms_loan must provide the reference LO rule")

        structure = Structure.create({
            'name': 'Loan Arming Test Structure',
            'type_id': template.struct_id.type_id.id,
        })
        self.assertFalse(structure._loan_recovery_rule())

        created = structure._arm_loan_recovery()
        self.assertEqual(len(created), 1)
        self.assertEqual(created.code, 'LO')
        self.assertEqual(created.struct_id, structure)
        self.assertEqual(created.condition_select, 'python')

        # idempotent: a second call creates nothing
        self.assertFalse(structure._arm_loan_recovery())
        self.assertEqual(len(structure._loan_recovery_rule()), 1)
