/** @odoo-module **/

/**
 * Opens the Company Policy popup in a dialog window.
 */

import { HrDashboard } from "@ent_hrms_dashboard/js/hrms_dashboard";
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(HrDashboard.prototype, {
    /**
     * Open the Company Policy form in a dialog window.
     *
     * Triggered from dashboard_view.xml using t-on-click.
     */
    actionOpenCompanyPolicy() {
        this.action.doAction({
            name: _t("Company Policy"),
            type: 'ir.actions.act_window',
            res_model: 'res.company.policy',
            view_mode: 'form',
            views: [[false, 'form']],
            context: {
                'default_company_id': session.company_id,
            },
            target: 'new',
        });
    },
});