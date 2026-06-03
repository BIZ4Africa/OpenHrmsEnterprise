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
from odoo import api, fields, models


class HREmployee(models.Model):
    """Inherits the model hr.employee"""
    _inherit = 'hr.employee'

    @api.depends('exit_checklist_ids')
    def _compute_exit_progress(self):
        """This is used to determine the exit status"""
        for each in self:
            total_len = self.env['employee.checklist'].search_count(
                [('document_type', '=', 'exit')])
            entry_len = len(each.exit_checklist_ids)
            if total_len != 0:
                each.exit_progress = (entry_len * 100) / total_len

    @api.depends('entry_checklist_ids')
    def _compute_entry_progress(self):
        """This is used to determine the entry status"""
        for each in self:
            total_len = self.env['employee.checklist'].search_count(
                [('document_type', '=', 'entry')])
            entry_len = len(each.entry_checklist_ids)
            if total_len != 0:
                each.entry_progress = (entry_len * 100) / total_len

    entry_checklist_ids = fields.Many2many('employee.checklist', 'entry_obj_ids',
                                           'check_hr_rel', 'hr_check_rel',
                                           string='Entry Process',
                                           domain=[
                                               ('document_type', '=', 'entry')],
                                           help="Entry Checklist's")
    exit_checklist_ids = fields.Many2many('employee.checklist', 'exit_obj_ids',
                                          'exit_hr_rel', 'hr_exit_rel',
                                          string='Exit Process',
                                          domain=[
                                              ('document_type', '=', 'exit')],
                                          help="Exit Checklists")
    entry_progress = fields.Float(compute=_compute_entry_progress, string='Entry '
                                                                 'Progress',
                                  store=True, default=0.0,
                                  help="Percentage of Entry Checklist's")
    exit_progress = fields.Float(compute=_compute_exit_progress, string='Exit Progress',
                                 store=True, default=0.0,
                                 help="Percentage of Exit Checklist's")
    maximum_rate = fields.Integer(default=100, string='Maximum Rate',
                                  help='Maximum rate of Entry Checklist')
    check_list_enable = fields.Boolean(copy=False,
                                       string='Enable Checklist',
                                       help="Checklist is enabled")
