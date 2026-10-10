## Module <ent_ohrms_salary_advance>

#### 27.02.2025
#### Version 18.0.1.0.0
##### ADD
- Initial commit for Enterprise OpenHRMS Salary Advance

#### 10.10.2026
#### Version 1.0.2
##### FIX
- `ir.sequence.get()` **does not exist in 19.0** (the alias was removed after
  18.0; `next_by_code` / `next_by_id` are the APIs of the series). `create()`
  still called it, and **no module of the 19.0 chain overrides
  `salary.advance.create`** (`hr_loan_advanced` extends the model but defines no
  `create`): the call is therefore on the path, and creating a salary advance
  raised `AttributeError: 'ir.sequence' object has no attribute 'get'`.
- The call is translated to `next_by_code`, which is the whole fix here: this
  module's sequence is declared with `company_id = False`, so `next_by_code`
  (which looks at `company_id IN (current company, NULL)`) finds it from every
  company — no per-company series is needed. This is exactly what the 18.0
  series measured (commit `0b29b2b`), where the translation was kept while the
  loan series was rewritten per company.
- The behaviour is otherwise unchanged: the `or ' '` fallback is kept, as in
  the 18.0 series for this module.

#### 10.10.2026
#### Version 1.0.3
##### FIX
- **No free `name` on the accounting entry of a salary advance** (port of the
  18.0 work `18.0.1.0.2` / commit `286cc87`). `action_approve_request_acc_dept`
  wrote `'name': 'Salary Advance Of ' + ' ' + request_name` on the
  `account.move`. Odoo never renumbers an entry that already carries a name
  (`account.move._compute_name`), and the journal numbering
  (`sequence.mixin._get_last_sequence` / `_locked_increment`) then adopted that
  free name as its numbering **template** for every following entry. Measured
  on SPORTS EXPERTS (company 2, journal `BNK1`, 2026-10-08): the three entries
  of ANOTHER employee's loan showed up under
  `'Salary Advance Of  Ilunga Mwamba Patrick1/2/3'`, and the next entry of the
  journal was already `'...Patrick4'` — the bank journal had no usable entry
  numbering left.
- The entry number is now left to the journal (`BNK1/2026/0000N`); the human
  label lives in `ref` and follows a **configurable** template
  (`ir.config_parameter` `ent_ohrms_salary_advance.move_ref_template`,
  placeholders `{reference}` `{employee}` `{company}`, default
  `Salary advance {reference} for {employee}`, same shape as `ent_loan_accounting`'s
  `Loan LO/0001 for <employee>`). A broken template falls back to the default
  instead of blocking a payroll operation.
- Non-regression tests ported from 18.0
  (`tests/test_salary_advance_move_name.py`): the entry number follows the
  journal numbering, the name of one employee can never appear on another
  employee's entry, and the `ref` follows the template.
- **`security/salary_advance_security.xml` is now declared** in the manifest's
  `data` key. The file was present in the 19.0 tree but **not declared**, so it
  was inert: the three `ir.rule` it carries (multi-company, HR/accounting
  officer, employee-own-records) were never loaded in 19.0 — the 18.0
  manifest declares them. Every xmlid the file resolves
  (`model_salary_advance`, `hr.group_hr_user`, `account.group_account_user`,
  `base.group_user`) is defined in the 19.0 series.
