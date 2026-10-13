## Module <ent_history_employee>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ir.model.access.csv` is declared again in the manifest. Commit
  `900b76a` ("Remove orphaned string continuations from 25 manifests") dropped
  the declaration while the file stayed in the tree, so nothing loaded it:
  - `access_department_history_user` -> `model_department_history`: read for
    `base.group_user`
  - `access_salary_history_user` -> `model_salary_history`: read for
    `base.group_user`
  - `access_timesheet_cost_user` -> `model_timesheet_cost`: read for
    `base.group_user`
  - `access_contract_history_user` -> `model_contract_history`: read for
    `base.group_user`
  - `access_department_history_manager` -> `model_department_history`: read,
    write, create, unlink for `hr.group_hr_manager`
  - `access_salary_history_manager` -> `model_salary_history`: read, write,
    create, unlink for `hr.group_hr_manager`
  - `access_contract_history_manager` -> `model_contract_history`: read, write,
    create, unlink for `hr.group_hr_manager`
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 19.03.2025 
#### Version 18.0.1.0.0
##### ADD
- Initial Commit for Enterprise Open HRMS Employee History



