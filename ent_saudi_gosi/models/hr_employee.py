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


class HrEmployee(models.Model):
    """Inherited hr_employee to add new fields"""
    _inherit = 'hr.employee'

    type = fields.Selection([('saudi', 'Saudi')], string='Type',
                            help="Select the type")
    gosi_number = fields.Char(string='GOSI Number', help="Enter Gosi Number")
    issue_date = fields.Date(string='Issued Date', help="Choose Issued Date")
    age = fields.Char(string='Age', help="Enter Age")
    limit = fields.Boolean(string='Eligible For GOSI', compute='_compute_age',
                           default=False,
                           help="Eligibility for GOSI")

    @api.depends('age')
    def _compute_age(self):
        """Check age for gosi eligibility"""
        for res in self:
            if 60 >= int(res.age) >= 18:
                res.limit = True
            else:
                res.limit = False
