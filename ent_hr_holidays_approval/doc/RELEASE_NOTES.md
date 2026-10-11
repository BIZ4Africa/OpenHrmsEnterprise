## Module <ent_holiday_approval>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ent_hr_holiday_approval_security.xml` is declared again in the
  manifest. Commit `900b76a` ("Remove orphaned string continuations from 25
  manifests") dropped the declaration while the file stayed in the tree, so
  nothing loaded it:
  - 1 `ir.rule`: `property_rule_holidays_employee` (name=Employee Leaves,
    model_id=model_hr_leave)
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 09.08.2025
#### Version 18.0.1.0.0
##### ADD
- Initial commit for Enterprise Open HRMS Leave Multi-Level Approval
