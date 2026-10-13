## Module <ent_hr_zk_attendance>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ir.model.access.csv` is declared again in the manifest. Commit
  `900b76a` ("Remove orphaned string continuations from 25 manifests") dropped
  the declaration while the file stayed in the tree, so nothing loaded it:
  - `access_zk_machine_officer` -> `model_zk_machine`: read, write, create,
    unlink for `hr_attendance.group_hr_attendance_officer`
  - `access_zk_machine_attendance_officer` -> `model_zk_machine_attendance`:
    read, write, create, unlink for `hr_attendance.group_hr_attendance_officer`
  - `access_zk_report_daily_attendance_officer` ->
    `model_zk_report_daily_attendance`: read, write, create, unlink for
    `hr_attendance.group_hr_attendance_officer`
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 17.03.2026
#### Version 18.0.1.0.0
##### ADD
- Initial commit for Enterprise HRMS Biometric Device Integration
