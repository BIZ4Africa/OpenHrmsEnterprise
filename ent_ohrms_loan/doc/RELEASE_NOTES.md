## Module <ent_ohrms_loan>

#### 19.03.2025
#### Version 18.0.1.0.0
##### ADD

- Initial commit for Enterprise OpenHRMS Loan Management

#### 09.10.2026
#### Version 18.0.1.0.3
##### FIX

- Loan reference (``hr.loan.name``) is no longer created blank in a company
  other than the one that owned the single, company-less sequence. One
  ``hr.loan.seq`` sequence is now provisioned per company (post-init hook and
  ``migrations/1.0.3``), each bound to its own company, with a configurable
  prefix (``ent_ohrms_loan.loan_sequence_prefix``, per-company override
  ``..._<company_id>``). A reference supplied by the caller is preserved.
- A missing sequence is now a logged error raised to the user instead of a
  silent ``or ' '`` fallback, which is what kept the blank names (and the
  unreadable ``Loan   for <employee>`` accounting labels) invisible.
- ``migrations/1.0.3`` names the loans left with a blank reference from the
  sequence of their own company; no accounting entry is modified.
