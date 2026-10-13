## Module <ent_ohrms_service_request>

#### 13.10.2026
#### Version 1.0.3
##### FIX

- `product` is declared in `depends`. `models/service_request.py` declares
  `service_product_id = fields.Many2one('product.product')` (also used by
  `views/service_request_views.xml` and by the report values), but the 19.0
  manifest did not pull `product` in — the 18.0 manifest depended on `stock`,
  which brought it. When `product` is not installed, loading the model raises

      AssertionError: Field service.request.service_product_id with unknown comodel_name 'product.product'

  and the module cannot be installed. Counter-measure: fresh database,
  `-i ent_ohrms_service_request` -> `exit=0`, module `installed 1.0.3`, no
  ERROR/CRITICAL line.

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
