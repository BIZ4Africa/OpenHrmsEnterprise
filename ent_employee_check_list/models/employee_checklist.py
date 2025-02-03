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
from odoo import fields, models


class EmployeeChecklist(models.Model):
    _name = 'employee.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Documents"
    _order = 'sequence'

    name = fields.Char(string='Name', copy=False, required=1,
                       help="Checklist Name")
    document_type = fields.Selection([('entry', 'Entry Process'),
                                      ('exit', 'Exit Process'),
                                      ('other', 'Other')],
                                     string='Checklist Type',
                                     help='Type of Checklist',
                                     required=1)
    sequence = fields.Integer(string='Sequence', help="Sequence of Checklist")
    entry_obj = fields.Many2many('hr.employee', 'entry_checklist',
                                 'hr_check_rel', 'check_hr_rel',
                                 invisible=1, string="Entry Object")
    exit_obj = fields.Many2many('hr.employee', 'exit_checklist', 'hr_exit_rel',
                                'exit_hr_rel', string="Exit Object",
                                invisible=1)
    entry_obj_plan = fields.Many2many('hr.employee', 'entry_checklist_plan_ds',
                                      'hr_check_rel', 'check_hr_rel',
                                      invisible=1, string="Plan Object")
    exit_obj_plan = fields.Many2many('hr.employee', 'exit_checklist_plan_ids',
                                     'hr_exit_rel', 'exit_hr_rel',
                                     invisible=1, string='Exit Plan Object')
