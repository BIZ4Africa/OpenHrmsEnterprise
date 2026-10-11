## Module <ent_hr_employee_shift>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ir.model.access.csv` is declared again in the manifest. Commit
  `900b76a` ("Remove orphaned string continuations from 25 manifests") dropped
  the declaration while the file stayed in the tree, so nothing loaded it:
  - `access_hr_shift_schedule_manager` -> `model_hr_shift_schedule`: read,
    write, create, unlink for `hr.group_hr_manager`
  - `access_hr_shift_generate_manager` -> `model_hr_shift_generate`: read,
    write, create, unlink for `hr.group_hr_manager`
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 09.08.2025
#### Version 18.0.1.0.0
##### ADD
- Initial commit for Enterprise Open HRMS Employee Shift
