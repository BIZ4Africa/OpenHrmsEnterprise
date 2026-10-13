## Module <ent_hr_reward_warning>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/hr_announcement_security.xml` is declared again in the manifest.
  Commit `900b76a` ("Remove orphaned string continuations from 25 manifests")
  dropped the declaration while the file stayed in the tree, so nothing loaded
  it:
  - 1 `ir.rule`: `hr_announcement_rule_user` (name=Announcement Multi Company,
    model_id=model_hr_announcement, global=True)
  - 1 `ir.module.category`: `ir_module_category_announcement`
    (name=Announcement)
  - 2 `res.groups.privilege`: `res_groups_employee_privilege` (name=Employee),
    `res_groups_administrator_privilege` (name=Administrator)
  - 2 `res.groups`: `res_groups_employee` (name=Employee,
    privilege_id=res_groups_employee_privilege), `res_groups_administrator`
    (name=Administrator, privilege_id=res_groups_administrator_privilege)
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 15.11.2024
#### Version 18.0.1.0.0
##### ADD

- Initial commit for Enterprise OpenHRMS Official Announcements
