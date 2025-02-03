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
from odoo import models


class MailActivitySchedule(models.TransientModel):
    _inherit = 'mail.activity.schedule'

    def action_schedule_plan(self):
        """
        Function is override for appending checklist values
        to the mail activity.

        """
        employee = self.env['hr.employee'].browse(
            self._context.get('active_id'))
        check_type_id = self.env.ref(
            'ent_employee_check_list.checklist_activity_type')
        on_id = self.env.ref('hr.onboarding_plan')
        of_id = self.env.ref('hr.offboarding_plan')
        for activity_type in self.plan_id.template_ids:
            responsible = activity_type.responsible_id
            if self.env['hr.employee'].with_user(
                    responsible).check_access_rights('read',
                                                     raise_exception=False):
                self.env['mail.activity'].create({
                    'res_id': self._context.get('active_id'),
                    'res_model_id': employee.env['ir.model']._get(
                        'hr.employee').id,
                    'summary': activity_type.summary,
                    'note': self.note,
                    'activity_type_id': self.activity_type_id.id,
                    'user_id': self.activity_user_id.id,
                    'entry_checklist_plan_ids': activity_type.entry_checklist_plan_ids,
                    'exit_checklist_plan_ids': activity_type.exit_checklist_plan_ids,
                    'check_type_check': True if activity_type.id == check_type_id.id else False,
                    'on_board_type_check': True if self.plan_id.id == on_id.id else False,
                    'off_board_type_check': True if self.plan_id.id == of_id.id else False
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self._context.get('active_id'),
            'name': self.env['hr.employee'].browse(
                self._context.get('active_id')).display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }
