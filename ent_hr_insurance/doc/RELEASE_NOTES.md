## Module <ent_hr_insurance>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ent_hr_insurance_security.xml` is declared again in the manifest.
  Commit `900b76a` ("Remove orphaned string continuations from 25 manifests")
  dropped the declaration while the file stayed in the tree, so nothing loaded
  it:
  - 2 `ir.rule`: `property_rule_hr_shift` (name=Hr Insurancy Company,
    model_id=model_hr_insurance, global=True),
    `property_rule_hr_shift_generate` (name=Employee Insurance Policy company,
    model_id=model_insurance_policy, global=True)
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 19.03.2025
#### Version 18.0.1.0.0
##### ADD
- Initial commit for Enterprise Open HRMS Employee Insurance
