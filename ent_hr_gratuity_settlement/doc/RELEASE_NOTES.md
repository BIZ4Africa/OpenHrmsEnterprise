## Module <ent_hr_gratuity_settlement>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ir.model.access.csv` is declared again in the manifest. Commit
  `900b76a` ("Remove orphaned string continuations from 25 manifests") dropped
  the declaration while the file stayed in the tree, so nothing loaded it:
  - `access_hr_gratuity_manager` -> `model_hr_gratuity`: read, write, create,
    unlink for `hr.group_hr_manager`
  - `access_hr_gratuity_officer` -> `model_hr_gratuity`: read, write, create,
    unlink for `hr.group_hr_user`
  - `access_hr_gratuity_accounting_configuration_manager` ->
    `model_hr_gratuity_accounting_configuration`: read, write, create, unlink
    for `hr.group_hr_manager`
  - `access_hr_gratuity_accounting_configuration_officer` ->
    `model_hr_gratuity_accounting_configuration`: read, write, create, unlink
    for `hr.group_hr_user`
  - `access_gratuity_configuration_officer` -> `model_gratuity_configuration`:
    read for `hr.group_hr_user`
  - `access_gratuity_configuration_manager` -> `model_gratuity_configuration`:
    read, write, create, unlink for `hr.group_hr_manager`
  - `access_hr_training_user` -> `model_hr_training`: read, write, create,
    unlink for `base.group_user`
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 26.03.2025
#### Version 18.0.1.0.0
##### ADD
- Initial Commit for Enterprise Open HRMS Gratuity Settlement
