## Module <ent_loan_accounting>

#### 08.10.2026
#### Version 18.0.1.0.7
##### FIX

- Loan disbursement ('octroi') direction: the entry is now
  **D loan receivable / C treasury**. The 1.0.6 release debited the treasury
  and credited the payroll payable, which inflated the bank balance by the loan
  amount and overstated the salary due (measured on the SPORTS EXPERTS
  instance, move 32: D 521001 300 000 / C 422000 300 000).
- Payslip recovery direction: the entry is now
  **D payroll payable / C loan receivable**. 1.0.6 credited the treasury, i.e.
  credited the bank a second time.
- New required field `loan_account_id` ("Loan Account") on `hr.loan`: the
  receivable account carrying the employee loan. The three accounts (employee,
  loan, treasury) must be distinct.
- `migrations/1.0.7/post-migrate.py` back-fills `loan_account_id` on existing
  loans from the company chart (codes 421100 / 4211), so an upgraded database
  stays usable. The back-fill itself lives on the model
  (`hr.loan._backfill_loan_account`) and is covered by the module tests.
- Arming the payslip recovery on a company that runs its own payroll structures
  is **opt-in**: `hr.payroll.structure._arm_loan_recovery()` copies the
  reference `LO` rule onto the structures of a company, and the migration only
  calls it when the system parameter
  `ent_loan_accounting.arm_loan_recovery_company_<company_id>` is set. A
  structure that already deducts loans through a competing rule code (`LOAN`,
  used by the DRC payroll bridge `l10n_cd_hr_payroll_loan_bridge`) is
  deliberately **left untouched** — arming `LO` next to it would deduct the
  same installment twice.
- Non-regression tests: `tests/test_loan_accounting_direction.py` fails if
  either leg flips back, or if the `LO` rule is armed on a structure that
  already deducts loans through a competing rule.

#### 26.03.2025
#### Version 18.0.1.0.0
##### ADD

- Initial commit for Enterprise OpenHRMS Loan Accounting
