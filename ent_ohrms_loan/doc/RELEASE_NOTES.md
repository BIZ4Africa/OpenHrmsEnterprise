## Module <ent_ohrms_loan>

#### 19.03.2025
#### Version 18.0.1.0.0
##### ADD

- Initial commit for Enterprise OpenHRMS Loan Management 

#### 10.10.2026
#### Version 1.0.2
##### FIX

- `ir.sequence.get()` **does not exist in 19.0** (the alias was removed after
  18.0; `next_by_code` / `next_by_id` are the APIs of the series): the `create`
  of this module still called it, so creating a loan raised
  `AttributeError: 'ir.sequence' object has no attribute 'get'` on every base
  where this module owns `hr.loan.create` (i.e. when `hr_loan_advanced` is not
  installed -- that module calls `super(OpenHrmsLoan, self).create(...)`, a
  lookup that starts AFTER this module's `create`).
- The call is not translated to `next_by_code` alone: the 18.0 series measured
  that translation insufficient and rewrote the reference series (work
  `ent_ohrms_loan 1.0.3`, manifest `1.0.4`, commit `04a2d29`), and that work is
  ported here:

  * ``_ensure_loan_sequences()`` provisions one ``hr.loan.seq`` sequence **per
    company**, each bound to its own company (idempotent). The historical XML
    record had no ``company_id``, so Odoo bound it to the company active at
    installation: `next_by_code` only looks at ``company_id IN (current
    company, NULL)``, so every other company found no series and its loans
    were created with a blank name (' ') and unreadable accounting labels
    ("Loan   for <employee>").
  * called by the ``post_init`` hook at installation and by
    ``migrations/1.0.2/post-migrate.py`` at upgrade (a post-init hook is never
    called on update);
  * configurable prefix: ``ent_ohrms_loan.loan_sequence_prefix`` (default
    ``LO/``) with a per-company override
    ``ent_ohrms_loan.loan_sequence_prefix_<company_id>``;
  * ``create()`` draws the reference from the sequence of **the loan's own
    company** (not of the ambient company), never overwrites a reference
    supplied by the caller, and **raises** a visible ``UserError`` when the
    sequence is missing instead of the silent ``or ' '`` fallback that kept
    the blank names invisible;
  * ``migrations/1.0.2`` names the loans left with a blank reference, from the
    sequence of their own company. Only ``hr.loan.name`` is written: no
    accounting entry is modified.
  * ``data/ir_sequence_data.xml`` no longer declares a sequence without
    ``company_id`` (the source of the binding to the installation company).
    Removing an XML record never deletes an existing row, so nothing already
    installed is lost.

##### Versioning

- The 19.0 lineage is distinct from the 18.0 one (``1.0.1`` here against
  ``1.0.4`` there): the version of this port follows its **own** lineage
  (``1.0.1`` -> ``1.0.2``) so that the migration directory is reached by the
  kernel's loader on an installed base.

##### Tests

- ``tests/test_hr_loan_sequence.py``: non-regression (a blank reference is
  impossible in company 2, a missing sequence is a visible error, the
  provisioning is idempotent, a caller-supplied reference is preserved). The
  class is skipped, with a named reason, when another installed module owns
  ``hr.loan.create`` -- the guarantee is then not this module's to make.
