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
#
################################################################################
"""Non-regression tests for the accounting entry of a salary advance.

Measured defect (SPORTS EXPERTS, journal BNK1, 2026-10-08): the module wrote a
FREE ``name`` on the journal entry (``'Salary Advance Of  <employee>'``). Odoo
then skipped the journal numbering for that entry, and the journal adopted the
free name as its numbering TEMPLATE for every following entry -- so the loan
entries of ANOTHER employee (300 000) showed up under that name, and the next
entry of the journal was already named ``'...Patrick4'``.

The tests below fail whenever:
  * the entry number is not the journal's own numbering (free name), or
  * the entry name of employee A carries the name of employee B, or
  * the reference is not built from the configurable template.
"""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

REF_TEMPLATE_PARAM = 'ent_ohrms_salary_advance.move_ref_template'
REF_TEMPLATE_DEFAULT = 'Salary advance {reference} for {employee}'


@tagged('post_install', '-at_install')
class TestSalaryAdvanceMoveName(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref('base.main_company')
        cls.env = cls.env(context=dict(cls.env.context,
                                       allowed_company_ids=[cls.company.id]))
        cls.journal = cls.env['account.journal'].create({
            'name': 'Advance Move Name Test',
            'code': 'AMNT',
            'type': 'bank',
            'company_id': cls.company.id,
        })
        cls.debit_account = cls.journal.default_account_id
        cls.credit_account = cls.journal.suspense_account_id
        cls.employee_a = cls.env['hr.employee'].create({
            'name': 'Advance Employee A', 'company_id': cls.company.id})
        cls.employee_b = cls.env['hr.employee'].create({
            'name': 'Advance Employee B', 'company_id': cls.company.id})

    def _approve_advance(self, employee, date):
        advance = self.env['salary.advance'].create({
            'employee_id': employee.id,
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'advance': 100.0,
            'date': date,
            'journal_id': self.journal.id,
            'debit_id': self.debit_account.id,
            'credit_id': self.credit_account.id,
        })
        advance.action_approve_request_acc_dept()
        move = self.env['account.move'].search([
            ('journal_id', '=', self.journal.id),
            ('ref', 'ilike', employee.name),
        ], limit=1)
        self.assertTrue(move, 'no accounting entry was produced')
        return advance, move

    def test_entry_name_is_the_journal_numbering(self):
        """The entry number comes from the journal, never from a free name."""
        advance, move = self._approve_advance(self.employee_a, '2032-01-15')
        expected_prefix = self.journal.code + '/'
        self.assertTrue(
            move.name.startswith(expected_prefix),
            'entry name %r is not the journal numbering (%s*)'
            % (move.name, expected_prefix))
        self.assertNotIn('Salary Advance Of', move.name or '')
        self.assertNotIn(self.employee_a.name, move.name or '')
        self.assertEqual(
            move.ref,
            'Salary advance %s for %s' % (advance.name, self.employee_a.name))
        # the journal chain keeps its own numbering for the next entry
        probe = self.env['account.move'].new(
            {'journal_id': self.journal.id, 'date': move.date})
        last = probe._get_last_sequence()
        self.assertTrue(
            last.startswith(expected_prefix),
            'the journal chain is anchored on %r, not on %s*'
            % (last, expected_prefix))
        self.assertNotIn('Salary Advance Of', last or '')

    def test_other_employee_name_never_leaks(self):
        """The entry of employee A never carries employee B's name."""
        _adv_a, move_a = self._approve_advance(self.employee_a, '2032-01-15')
        _adv_b, move_b = self._approve_advance(self.employee_b, '2032-02-15')
        self.assertNotEqual(move_a.id, move_b.id)
        for move, other in ((move_a, self.employee_b), (move_b, self.employee_a)):
            self.assertNotIn(other.name, move.name or '')
            self.assertNotIn(other.name, move.ref or '')

    def test_ref_follows_the_configurable_template(self):
        """The label is a configurable template, not a hard-coded string."""
        self.env['ir.config_parameter'].sudo().set_param(
            REF_TEMPLATE_PARAM, 'Avance {reference} / {employee} ({company})')
        advance, move = self._approve_advance(self.employee_a, '2032-03-15')
        self.assertEqual(
            move.ref,
            'Avance %s / %s (%s)'
            % (advance.name, self.employee_a.name, self.company.name))

    def test_broken_template_does_not_block_a_payroll_operation(self):
        """A broken template falls back to the default label."""
        self.env['ir.config_parameter'].sudo().set_param(
            REF_TEMPLATE_PARAM, 'Avance {unknown_placeholder}')
        advance, move = self._approve_advance(self.employee_a, '2032-04-15')
        self.assertEqual(
            move.ref,
            REF_TEMPLATE_DEFAULT.format(
                reference=advance.name, employee=self.employee_a.name))
