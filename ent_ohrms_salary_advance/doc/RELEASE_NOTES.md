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
