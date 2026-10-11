## Module <ent_employee_background>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ir.model.access.csv` is declared again in the manifest. Commit
  `900b76a` ("Remove orphaned string continuations from 25 manifests") dropped
  the declaration while the file stayed in the tree, so nothing loaded it:
  - `access_employee_verification_manager` -> `model_employee_verification`:
    read, write, create, unlink for `hr.group_hr_manager`
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 01.03.2025
#### Version 19.0.1.0.0
#### ADD
- Initial commit for Enterprise OHRMS Employee Background
