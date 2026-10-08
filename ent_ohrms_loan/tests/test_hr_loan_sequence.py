# -*- coding: utf-8 -*-
"""Non-regression: a loan reference is never blank, and it comes from the
sequence of the loan's own company."""
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestHrLoanSequence(TransactionCase):
    """Loan references and the per-company sequence."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env.ref('base.main_company')
        cls.company_b = cls.env['res.company'].create({
            'name': 'Loan sequence test company'})
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Loan sequence test employee',
            'company_id': cls.company_b.id,
        })

    def _loan_values(self, company, **overrides):
        values = {
            'employee_id': self.employee.id,
            'company_id': company.id,
            'currency_id': company.currency_id.id,
            'loan_amount': 1000.0,
            'installment': 1,
            'payment_date': '2031-01-31',
        }
        values.update(overrides)
        return values

    def test_loan_of_a_company_uses_its_own_sequence(self):
        """A loan created in company B is numbered from company B's series.

        This is the non-regression test of the blank-name defect: before the
        fix, a loan of any company other than the one that owned the unique
        sequence was created with name ' '.
        """
        self.env['hr.loan']._ensure_loan_sequences(self.company_b)
        loan = self.env['hr.loan'].with_company(self.company_b).create(
            self._loan_values(self.company_b))
        self.assertTrue(
            loan.name and loan.name.strip() and loan.name.strip() != '/',
            "a loan must never be created with a blank name, got %r"
            % loan.name)
        self.assertTrue(loan.name.startswith('LO/'),
                        "unexpected loan reference %r" % loan.name)
        # The reference belongs to company B, not to the ambient company.
        self.assertEqual(loan.company_id, self.company_b)

    def test_missing_sequence_is_a_visible_error(self):
        """A company without a sequence raises instead of naming the loan ' '."""
        self.env['hr.loan']._loan_sequence(self.company_b).unlink()
        with self.assertRaises(UserError):
            self.env['hr.loan'].with_company(self.company_b).create(
                self._loan_values(self.company_b))

    def test_an_existing_reference_is_not_overwritten(self):
        """A reference supplied by the caller (a dependent module) is kept."""
        self.env['hr.loan']._ensure_loan_sequences(self.company_b)
        loan = self.env['hr.loan'].with_company(self.company_b).create(
            self._loan_values(self.company_b, name='MANUAL-REF'))
        self.assertEqual(loan.name, 'MANUAL-REF')

    def test_ensure_loan_sequences_is_idempotent(self):
        """Provisioning twice never creates a duplicate series."""
        self.env['hr.loan']._ensure_loan_sequences(self.company_b)
        first = self.env['hr.loan']._loan_sequence(self.company_b)
        self.env['hr.loan']._ensure_loan_sequences(self.company_b)
        second = self.env['hr.loan']._loan_sequence(self.company_b)
        self.assertEqual(first, second)
        self.assertEqual(
            self.env['ir.sequence'].search_count(
                [('code', '=', 'hr.loan.seq'),
                 ('company_id', '=', self.company_b.id)]),
            1)
