# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################
from odoo import fields, models, _
from odoo.exceptions import UserError


class MailActivityPlanTemplate(models.Model):
    _inherit = 'mail.activity.plan.template'

    entry_checklist_plan_ids = fields.Many2many('employee.checklist',
                                                'entry_obj_plan',
                                                'check_hr_rel',
                                                'hr_check_rel',
                                                string='Entry Process',
                                                domain=[('document_type', '=',
                                                         'entry')])
    exit_checklist_plan_ids = fields.Many2many('employee.checklist',
                                               'exit_obj_plan', 'exit_hr_rel',
                                               'hr_exit_rel',
                                               string='Exit Process',
                                               domain=[
                                                   ('document_type', '=',
                                                    'exit')])

    def unlink(self):
        """
        Function is used for while deleting the planing types
        it check if the record is related to checklist and raise
        error.

        """
        check_id = self.env.ref(
            'ent_employee_check_list.checklist_activity_type')
        for recd in self:
            if recd.id == check_id.id:
                raise UserError(_("Checklist Record Can't Be Delete!"))
        return super().unlink()
