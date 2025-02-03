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
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'
    """Inheriting hr.leave to add more fields and functions"""

    leave_approvals_ids = fields.One2many('leave.validation.status',
                                          'holiday_id',
                                          string='Leave Validators',
                                          help="Leave approvals")

    is_multi_level_validation = fields.Boolean(
        string='Multiple Level Approval',
        compute="_compute_multi_level_approval",
        help="If checked then multi-level approval is necessary")

    is_button_visibility = fields.Boolean(default=True,
                                          compute="_compute_approval_details",
                                          string='Multiple Level Approval')

    @api.depends('holiday_status_id')
    def _compute_multi_level_approval(self):
        """Computes the multi level validation"""
        for rec in self:
            if rec.holiday_status_id.leave_validation_type == 'multi':
                rec.is_multi_level_validation = True
            else:
                rec.is_multi_level_validation = False

    def action_approve(self):
        """ Check if any pending tasks is added if so reassign the pending
        task else call approval """
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_(
                'Leave request must be confirmed ("To Approve")'
                ' in order to approve it.'))

        ohrmspro_vacation_project = self.sudo().env['ir.module.module'].search(
            [('name', '=', 'ohrmspro_vacation_project')],
            limit=1).state

        if ohrmspro_vacation_project == 'installed':
            return self.env['hr.leave'].check_pending_task(self)
        else:
            return self.approval_check()

    def approval_check(self):
        """ Check all leave validators approved the leave request if approved
         change the current request stage to Approved"""

        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

        active_id = self.env.context.get('active_id') if self.env.context.get(
            'active_id') else self.id

        user = self.env['hr.leave'].search([('id', '=', active_id)], limit=1)
        validation_obj = user.leave_approvals_ids.search(
            [('holiday_id', '=', user.id),
             ('validating_users_id', '=', self.env.uid)])
        validation_obj.is_validation_status = True
        approval_flag = True
        for user_obj in user.leave_approvals_ids:
            if not user_obj.is_validation_status:
                approval_flag = False
        if approval_flag:
            user.filtered(
                lambda hol: hol.validation_type == 'both').sudo().write(
                {'state': 'validate1',
                 'first_approver_id': current_employee.id})
            user.filtered(
                lambda hol:
                not hol.validation_type == 'both').sudo().action_validate()
            if not user.env.context.get('leave_fast_create'):
                user.activity_update()
            return True
        else:
            return False

    def action_refuse(self):
        """ Refuse the leave request if the current user is in
        validators list """
        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

        approval_access = False
        for user in self.leave_approvals_ids:
            if user.validating_users_id.id == self.env.uid:
                approval_access = True
        if approval_access:
            for holiday in self:
                if holiday.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_(
                        'Leave request must be confirmed '
                        'or validated in order to refuse it.'))

                if holiday.state == 'validate1':
                    holiday.sudo().write(
                        {'state': 'refuse',
                         'first_approver_id': current_employee.id})
                else:
                    holiday.sudo().write(
                        {'state': 'refuse',
                         'second_approver_id': current_employee.id})
                # Delete the meeting
                if holiday.meeting_id:
                    holiday.meeting_id.unlink()
                # If a category that created several holidays,
                # cancel all related
                holiday.linked_request_ids.action_refuse()
            self._remove_resource_leave()
            self.activity_update()
            validation_obj = self.leave_approvals_ids.search(
                [('holiday_id', '=', self.id),
                 ('validating_users_id', '=', self.env.uid)])
            validation_obj.is_validation_status = False
            return True
        else:
            for holiday in self:
                if holiday.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_(
                        'Leave request must be confirmed '
                        'or validated in order to refuse it.'))

                if holiday.state == 'validate1':
                    holiday.write({'state': 'refuse',
                                   'first_approver_id': current_employee.id})
                else:
                    holiday.write({'state': 'refuse',
                                   'second_approver_id': current_employee.id})
                # Delete the meeting
                if holiday.meeting_id:
                    holiday.meeting_id.unlink()
                # If a category that created several holidays,
                # cancel all related
                holiday.linked_request_ids.action_refuse()
            self._remove_resource_leave()
            self.activity_update()
            return True

    def action_draft(self):
        """ Reset all validation status to false when leave request
        set to draft stage"""
        for user in self.leave_approvals_ids:
            user.is_validation_status = False
        return super().action_draft()

    @api.onchange('holiday_status_id')
    def add_validators(self):
        """ Update the tree view and add new validators
        when leave type is changed in leave request form """
        list = []
        self.leave_approvals_ids = [(5, 0, 0)]
        validating_users_id = []
        for user in self.leave_approvals_ids:
            validating_users_id.append(user.validating_users_id.id)
        for user in self.holiday_status_id.leave_validators_ids.filtered(
                lambda l: l.holiday_validators_id.id not in validating_users_id):
            list.append((0, 0, {
                'validating_users_id': user.holiday_validators_id.id,
            }))
        self.leave_approvals_ids = list

    def _get_approval_requests(self):
        """ Action for Approvals menu item to show approval
        requests assigned to current user """
        current_uid = self.env.uid
        hr_holidays = self.env['hr.leave'].search([('state', '=', 'confirm')])
        approval = []
        for req in hr_holidays:
            for user in req.leave_approvals_ids.filtered(
                    lambda l: l.validating_users_id.id == current_uid):
                approval.append(req.id)
        value = {
            'domain': str([('id', 'in', approval)]),
            'view_mode': 'tree,form',
            'res_model': 'hr.leave',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Approvals'),
            'res_id': self.id,
            'target': 'current',
            'create': False,
            'edit': False,
        }
        return value

    @api.depends('holiday_status_id', 'leave_approvals_ids', 'state')
    def _compute_approval_details(self):
        type_leave = self.holiday_status_id.leave_validation_type
        if self.leave_approvals_ids:
            for rec in self.leave_approvals_ids.filtered(
                    lambda l: l.validating_users_id == self.env.user):
                if rec.is_validation_status and type_leave == 'multi':
                    rec.holiday_id.is_button_visibility = True
                else:
                    rec.holiday_id.is_button_visibility = False
        else:
            self.is_button_visibility = False


class LeaveValidationStatus(models.Model):
    """ Model for leave validators and their status for each leave request """
    _name = 'leave.validation.status'

    holiday_id = fields.Many2one('hr.leave', string="Holiday")

    validating_users_id = fields.Many2one('res.users',
                                          string='Leave Validators',
                                          help="Leave validators",
                                          domain="[('share','=',False)]")
    is_validation_status = fields.Boolean(string='Approve Status',
                                          readonly=True,
                                          default=False,
                                          track_visibility='always',
                                          help="Status of approval process")
    leave_comments = fields.Text(string='Comments',
                                 help="Comments for the validation")

    @api.onchange('validating_users_id')
    def prevent_change(self):
        """ Prevent Changing leave validators from leave request form """
        raise UserError(_(
            "Changing leave validators is not permitted. You can only change "
            "it from Leave Types Configuration"))
