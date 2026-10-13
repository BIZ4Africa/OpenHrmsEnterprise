## Module <ent_hr_leave_request_aliasing>

#### 11.10.2026
#### Version 1.0.2
##### FIX

- `data/mail_alias_data.xml` is declared again in the manifest. Commit
  `900b76a` ("Remove orphaned string continuations from 25 manifests") dropped
  the declaration while the file stayed in the tree, so nothing loaded it:
  - 1 `mail.alias`: `mail_alias_hr_leave` (alias_name=leave,
    alias_model_id=model_hr_leave)
  - the block is `noupdate="1"` (created once, never reset by an update)
- Version bumped on purpose: Odoo only reloads a module whose manifest version
  is greater than the installed one (`ir_module_module.update_list`:
  `parse_version(terp['version']) > parse_version(mod.latest_version)`), so
  without this bump the restored declarations would silently never reach the
  instances where the module is already installed.

#### 03.02.2025
#### Version 18.0.1.0.0
##### ADD

- Initial commit for Enterprise OpenHRMS Leave Request Aliasing
