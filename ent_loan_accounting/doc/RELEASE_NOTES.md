## Module <ent_loan_accounting>

#### 10.10.2026
#### Version 19.0.1.0.5
##### FIX

- Ported from the 18.0 work `ent_loan_accounting 18.0.1.0.7` (of which this is
  the 19.0 branch's own next version: the two lineages are distinct, `1.0.4`
  here against `1.0.6` there). Loan accounting entries carried the wrong
  direction on both legs:
  - disbursement ('octroi'): the entry is now **D loan receivable / C
    treasury**. The `1.0.4` release debited the treasury and credited the
    payroll payable, which inflated the bank balance by the loan amount and
    overstated the salary due.
  - payslip recovery (`hr.loan.line.action_paid_amount`): the entry is now
    **D payroll payable / C loan receivable**. `1.0.4` credited the treasury,
    i.e. credited the bank a second time.
- New required field `loan_account_id` ("Loan Account") on `hr.loan`: the
  receivable account carrying the employee loan. The three accounts (employee,
  loan, treasury) must be distinct; the guarantee is `_check_loan_accounts()`,
  called by both approval routes and by the recovery.
- `migrations/1.0.5/post-migrate.py` back-fills `loan_account_id` on existing
  loans from the company chart (codes 421100 / 4211) through
  `hr.loan._backfill_loan_account()`, so an upgraded database stays usable.
- The `loan_account_id` field is added to the Accounting page of the loan form.

Not ported from `18.0.1.0.7`: the opt-in arming of the 'LO' payslip deduction
rule (`hr.payroll.structure`), a distinct concern — named here so it is not
mistaken for done.

#### 26.03.2025
#### Version 18.0.1.0.0
##### ADD

- Initial commit for Enterprise OpenHRMS Loan Accounting
