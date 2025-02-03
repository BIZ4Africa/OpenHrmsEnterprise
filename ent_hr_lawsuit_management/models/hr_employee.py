# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Vishnu K P (odoo@cybrosys.com)
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


class HrLegalEmployeeMaster(models.Model):
    _inherit = 'hr.employee'
    """Class is inherited to add custom fields and methods"""

    legal_count = fields.Integer(compute='_compute_legal_count',
                                 string='# Legal Actions', help='Legal actions')

    def _compute_legal_count(self):
        """Compute the legal actions count for the given employee"""
        for each in self:
            legal_ids = self.env['hr.lawsuit'].search(
                [('employee_id', '=', each.id)])
            each.legal_count = len(legal_ids)

    def legal_view(self):
        """Returns a list of legal actions associated with the employee"""
        for employee in self:
            legal_ids = self.env['hr.lawsuit'].sudo().search(
                [('employee_id', '=', employee.id)]).ids
            return {
                'domain': str([('id', 'in', legal_ids)]),
                'view_mode': 'tree,form',
                'res_model': 'hr.lawsuit',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'name': _('Legal Actions'),
            }
