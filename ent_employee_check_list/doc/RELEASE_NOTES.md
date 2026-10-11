## Module <ent_employee_check_list>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ir.model.access.csv` is declared again in the manifest. Commit
  `900b76a` ("Remove orphaned string continuations from 25 manifests") dropped
  the declaration while the file stayed in the tree, so nothing loaded it:
  - `access_employee_checklist_user` -> `model_employee_checklist`: read,
    write, create, unlink for `hr.group_hr_user`
  - `access_employee_checklist_emp` -> `model_employee_checklist`: read for
    `base.group_user`
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 16.03.2026
#### Version 18.0.1.0.0
##### ADD
- Initial Commit for Enterprise Open HRMS Employee Checklist
