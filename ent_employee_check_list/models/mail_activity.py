################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################
from odoo import fields, models


class MailActivity(models.Model):
    """Inherits the model mail.activity"""
    _inherit = 'mail.activity'

    entry_checklist_plan_ids = fields.Many2many('employee.checklist',
                                                'check_hr_rel', 'hr_check_rel',
                                                string='Entry Process',
                                                domain=[('document_type', '=',
                                                         'entry')],
                                                help="Entry Checklist's")
    exit_checklist_plan_ids = fields.Many2many('employee.checklist',
                                               'exit_hr_rel',
                                               'hr_exit_rel',
                                               string='Exit Process',
                                               domain=[
                                                   ('document_type', '=',
                                                    'exit')],
                                               help="Exit Checklist's")
    check_type_check = fields.Boolean(string="Activity Type Check",
                                      help="Activity Type Check for each "
                                           "activity")
    on_board_type_check = fields.Boolean(string="Onboarding",
                                         help="Onboarding activity")
    off_board_type_check = fields.Boolean(string="Off-boarding",
                                          help="Offboarding activity")

    def action_close_dialog(self):
        """
        Function is used for writing checklist values based on
        mail activity of the employee.
        """
        emp_checklist = self.env['hr.employee'].browse(self.res_id)
        emp_checklist.write({
            'entry_checklist_ids': self.entry_checklist_plan_ids if self.entry_checklist_plan_ids else emp_checklist.entry_checklist_ids,
            'exit_checklist_ids': self.exit_checklist_plan_ids if self.exit_checklist_plan_ids else emp_checklist.exit_checklist_ids
        })
        return super().action_close_dialog()
