## Module <ent_ohrms_service_request>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `security/ent_ohrms_service_request_security.xml` is declared again in the
  manifest. Commit `900b76a` ("Remove orphaned string continuations from 25
  manifests") dropped the declaration while the file stayed in the tree, so
  nothing loaded it:
  - 2 `ir.rule`: `request_visibility` (name=Request Visibility,
    model_id=model_service_request), `admin_visibility` (name=Administrator
    Visibility, model_id=model_service_request)
  - 1 `ir.module.category`: `module_service_execution` (name=Service)
  - 1 `res.groups.privilege`: `service_group_executer_privilege` (name=Service
    Executer)
  - 1 `res.groups`: `service_group_executer` (name=Service Executer,
    privilege_id=service_group_executer_privilege)
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 19.03.2025
#### Version 18.0.1.0.0
##### ADD
- Initial commit for Enterprise Open HRMS Service Request
