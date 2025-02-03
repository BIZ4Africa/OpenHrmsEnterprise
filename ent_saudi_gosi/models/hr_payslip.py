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
from odoo import fields, api, models, _


class HrPayslip(models.Model):
    """Inherited hr_payslip to add new fields"""
    _inherit = 'hr.payslip'

    gosi_no = fields.Many2one('gosi.payslip',
                              string='GOSI Reference', readonly=True,
                              help="Choose/Create Gosi Number")

    @api.onchange('employee_id')
    def onchange_employee_ref(self):
        """Check Employee and Fetch Gosi Ref"""
        for rec in self:
            gosi_no = rec.env['gosi.payslip'].search(
                [('employee_id', '=', rec.employee_id.id)])
            rec.gosi_no = gosi_no.id
