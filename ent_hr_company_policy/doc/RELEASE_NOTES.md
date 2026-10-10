## Module <ent_hr_company_policy>

#### 10.10.2026
#### Version 1.0.2
##### FIX
- **The dashboard patch is declared again**: `static/src/js/company_policy.js`
  is back in `web.assets_backend`. The file was present and unchanged in the
  19.0 tree but **not declared**, so it was never served: the "Company Policy"
  button that `static/src/xml/dashboard_view.xml` (declared) injects into
  `HrDashboardMain` with `t-on-click="actionOpenCompanyPolicy"` called a method
  that did not exist on `HrDashboard`.
- Measured on an installed 19.0 base (`web.assets_web.min.js`, which includes
  `web.assets_backend`), before the fix: the button ships (`1` occurrence of
  `actionOpenCompanyPolicy` in the template block) while
  `@ent_hr_company_policy/js/company_policy` is absent from the bundle (`0`),
  `HrDashboard.prototype.actionOpenCompanyPolicy` is `undefined` in the browser
  runtime, and calling it raises `TypeError: ... is not a function`. The
  dependency it patches, `@ent_hrms_dashboard/js/hrms_dashboard`, **is** served
  (`1`) — so the patch only had to be declared to work.
- The declaration had been dropped by commit `900b76a` ("Remove orphaned string
  continuations from 25 manifests"), which removed two asset entries while
  cleaning up unrelated string continuations; the 18.0 manifest declares this
  same `web.assets_backend` list with the `.js` first.

#### 24.04.2026
#### Version 18.0.1.0.0
##### ADD
- Initial commit for Enterprise HR Company Policy
