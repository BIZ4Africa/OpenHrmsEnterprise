# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#
########################################################################################
from odoo import models


class HrLeaveAllocationGenerateMultiWizard(models.TransientModel):
    """Compatibility alias for Odoo 17 wizard model rename.

    Some localization addons still inherit `hr.leave.allocation.generate.multi.wizard`
    from older Odoo versions. In Odoo 17, the base model is
    `hr.leave.allocation.generate.multi`.
    """

    _name = 'hr.leave.allocation.generate.multi.wizard'
    _inherit = 'hr.leave.allocation.generate.multi'
