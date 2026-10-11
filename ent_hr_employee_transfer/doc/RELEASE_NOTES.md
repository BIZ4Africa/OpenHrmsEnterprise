## Module <ent_hr_employee_transfer>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ent_hr_employee_transfer_security.xml` is declared again in the
  manifest. Commit `900b76a` ("Remove orphaned string continuations from 25
  manifests") dropped the declaration while the file stayed in the tree, so
  nothing loaded it:
  - 2 `ir.rule`: `employee_rule` (name=Employee Multi Company Rule,
    model_id=hr.model_hr_employee, global=True), `employee_contract_rule`
    (name=Contract Multi Company Rule, model_id=hr.model_hr_version,
    global=True)
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 31.01.2026
#### Version 18.0.1.0.0
##### ADD
- Initial commit for Enterprise Open HRMS Company Transfer

