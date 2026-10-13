## Module <ent_hr_lawsuit_management>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/security.xml` is declared again in the manifest. Commit `900b76a`
  ("Remove orphaned string continuations from 25 manifests") dropped the
  declaration while the file stayed in the tree, so nothing loaded it:
  - 1 `ir.module.category`: `module_lawsuit_category` (name=Lawsuit)
  - 2 `res.groups.privilege`: `law_manager_privilege` (name=Manager Law),
    `law_user_privilege` (name=User Law)
  - 2 `res.groups`: `law_manager` (name=Manager Law,
    privilege_id=law_manager_privilege), `law_user` (name=User Law,
    privilege_id=law_user_privilege)
  - 2 `ir.rule`: `law_suit_visibility_user` (name=User can only see his
    actions, model_id=model_hr_lawsuit), `law_suit_visibility_manager`
    (name=Admin can only see all actions, model_id=model_hr_lawsuit)
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 19.03.2025
#### Version 18.0.1.0.0
##### ADD

- Initial commit for Enterprise Open HRMS Legal Actions
