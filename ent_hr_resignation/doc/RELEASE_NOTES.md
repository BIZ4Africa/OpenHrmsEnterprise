## Module <ent_hr_resignation>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/hr_resignation_security.xml` is declared again in the manifest.
  Commit `900b76a` ("Remove orphaned string continuations from 25 manifests")
  dropped the declaration while the file stayed in the tree, so nothing loaded
  it:
  - 2 `ir.rule`: `hr_resignation_rule_user` (name=Employee Resignation User,
    model_id=ent_hr_resignation.model_hr_resignation),
    `hr_resignation_rule_manager` (name=Employee Resignation Manager,
    model_id=ent_hr_resignation.model_hr_resignation)
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 15.01.2025
#### Version 18.0.1.0.0
##### ADD
- Initial Commit for Enterprise OpenHRMS Resignation
