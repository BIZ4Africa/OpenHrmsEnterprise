## Module <ent_loan_accounting>

#### 09.10.2026
#### Version 18.0.1.0.9
##### FIX

- **Name of the recovery entry** (`hr.loan.line.action_paid_amount`, the
  OpenHRMS route): the module no longer forces the number of the accounting
  entry (`'LOAN/ <employee>/<month>'`). On Odoo 18 `account.sequence_mixin`
  reads a name as a *sequence*:
  - the entry is **refused** as soon as a group of digits of the label does not
    match the entry date — measured on SPORTS EXPERTS, journal BNK1:
    `ValidationError: The Date (10/09/2026) … isn't aligned with the existing
    sequence number (LOAN/ DIAG W17 lot F (a supprimer)/DIAG-lot-F)` (the `17`
    of `W17` read as a year) — card t_0f8e2a4e;
  - the journal **adopts** the label as its numbering TEMPLATE: Odoo never
    renumbers an entry that carries a name, so the next entry of the journal
    was born from the loan label (measured locally: the entry following an
    installment was named `LOAN/ <employee>/premiere-tranche1`).
  The entry NUMBER now comes from the journal (`BNK1/2026/00005`); the human
  label lives in `ref` and on the entry lines, like the disbursement entry.
- **Configurable label**: `ir.config_parameter`
  `ent_loan_accounting.recovery_move_ref_template`, placeholders
  `{reference} {employee} {period} {company}`, default
  `'Loan {reference} for {employee} - {period}'`. A broken template falls back
  on the default instead of blocking a payroll operation.
- The accounting unit rule of 1.0.8 is unchanged (conversion at the entry date,
  loan currency carried when the journal allows it) — the two routes share
  `hr.loan._loan_company_currency_amount`.
- Non-regression tests: `tests/test_loan_recovery_move_name.py` fails if the
  entry of an installment cannot be posted on a **bank** journal, if its number
  is not the journal numbering, if the entry following it in the journal
  inherits a loan label, or if the label stops following its template.

#### 09.10.2026
#### Version 18.0.1.0.8
##### FIX

- **Accounting unit of the loan disbursement ('octroi')**: a loan expressed in
  a currency other than the company currency is no longer posted raw in the
  company currency. The two legs are converted at the rate of the entry date
  and the entry carries the loan currency (`currency_id` +
  `amount_currency`), exactly like the payslip entry that recovers the
  installments (`res.company.convert_from_legal_currency`).
  Measured on SPORTS EXPERTS 2026-10-09 (company 2 in USD, loan in CDF at
  2 265 CDF/USD): the entry was `D 421100 300 000 / C 521001 300 000` **USD**
  for a 300 000 CDF loan (132,45 USD) while the recovery posted 44,15 USD per
  installment — 299 867,55 USD of the receivable could never be settled, the
  receivable was not reconcilable (card t_c6e17a81).
- **Parametrable, per company** (Settings > Accounting): the switch
  `ent_loan_currency_conversion` (default: enabled) and the entry date
  `ent_loan_conversion_date` (accounting entry date / loan date / first
  installment date). Exposed on `res.config.settings`; the decision is a
  setting, not a redeployment. No manual step on an existing database: Odoo
  initialises a new column on the existing rows with the field default
  (measured on a throwaway Odoo 18 database — column dropped, then a plain
  `-u ent_loan_accounting` without any version change restores
  `ent_loan_currency_conversion = true` on the existing company row).
- The same rule applies to the alternative OpenHRMS recovery route
  (`hr.loan.line.action_paid_amount`), so the model does not carry two
  behaviours.
- A conversion without any rate in the database is **reported** in the log
  instead of staying silent (Odoo converts 1:1 in that case).
- `migrations/1.0.8/post-migrate.py` reports (read-only, never reposts) the
  loans whose already posted disbursement entry is not expressed in the loan
  currency: correcting an existing entry is an accounting decision.
- Non-regression tests: `tests/test_loan_currency_conversion.py` fails if an
  amount is posted without conversion, if the installments do not settle the
  converted disbursement, or if the switch / entry date settings are ignored.

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
