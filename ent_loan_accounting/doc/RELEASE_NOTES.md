## Module <ent_loan_accounting>

#### 17.10.2026
#### Version 19.0.1.0.6
##### FIX

- **Anti-double-deduction guard when arming the 'LO' payslip rule**
  (19.0 port of the 18.0 work `ent_loan_accounting 18.0.1.0.7`, commit
  `b93337bdee`): `hr.payroll.structure._arm_loan_recovery()` copies the
  reference `LO` deduction rule onto the structures of a company whose
  structures never carried it (a multi-company database runs its own copies).
  A structure that already deducts loans through a **competing rule code**
  (`COMPETING_LOAN_RULE_CODES = ('LOAN',)` — the DRC payroll bridge
  `l10n_cd_hr_payroll_loan_bridge`) is deliberately **left untouched**: arming
  `LO` next to it would deduct the same installment twice. The guard is traced
  at INFO (`_logger.info`, never WARNING) and the module test captures it, so a
  deliberately misconfigured structure never colours `install.log`.
- `migrations/1.0.6/post-migrate.py`: back-fills `loan_account_id` (idempotent,
  already run by 1.0.5) and arms the `LO` rule **only** on the companies that
  opted in through `ent_loan_accounting.arm_loan_recovery_company_<company_id>`.
  Nothing is armed by default.
- Non-regression tests: `tests/test_loan_accounting_direction.py` fails if
  either accounting leg flips back, if the `LO` rule is armed on a structure
  that already deducts loans through a competing rule, or if the arming stops
  being idempotent.

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

#### 26.03.2025
#### Version 18.0.1.0.0
##### ADD

- Initial commit for Enterprise OpenHRMS Loan Accounting
