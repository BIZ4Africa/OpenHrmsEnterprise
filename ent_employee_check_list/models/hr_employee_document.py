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
from odoo import api, fields, models


class HrEmployeeDocument(models.Model):
    _inherit = 'hr.employee.document'

    document_name = fields.Many2one('employee.checklist',
                                    string='Checklist Document',
                                    help='Choose the document in the '
                                         'checklist here.Automatically the '
                                         'checklist box become true')

    @api.model
    def create(self, vals):
        """Supering the create function"""
        result = super().create(vals)
        if result.document_name.document_type == 'entry':
            result.employee_ref.write(
                {'entry_checklist': [(4, result.document_name.id)]})
        if result.document_name.document_type == 'exit':
            result.employee_ref.write(
                {'exit_checklist': [(4, result.document_name.id)]})
        return result

    def unlink(self):
        """Supering the unlink method"""
        for result in self:
            if result.document_name.document_type == 'entry':
                result.employee_ref.write(
                    {'entry_checklist': [(5, result.document_name.id)]})
            if result.document_name.document_type == 'exit':
                result.employee_ref.write(
                    {'exit_checklist': [(5, result.document_name.id)]})
        res = super().unlink()
        return res
