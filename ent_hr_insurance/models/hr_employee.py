# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: VISHNU KP (odoo@cybrosys.com)
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
from datetime import datetime
from odoo import models, fields


class HrInsurance(models.Model):
    """Hr employee module to add the custom fields and methods"""
    _inherit = 'hr.employee'

    insurance_percentage = fields.Float(string="Company Percentage ",
                                        help="Company insurance percentage")
    deduced_amount_per_month = fields.Float(string="Salary deduced per month",
                                            compute="get_deduced_amount",
                                            help="Amount that is deduced f"
                                                 "rom the salary per month")
    deduced_amount_per_year = fields.Float(string="Salary deduced per year",
                                           compute="get_deduced_amount",
                                           help="Amount that is deduced from"
                                                " the salary per year")
    insurance = fields.One2many('hr.insurance', 'employee_id',
                                string="Insurance", help="Insurance",
                                domain=[('state', '=', 'active')])

    def get_deduced_amount(self):
        '''To get deduced amount'''
        current_date = datetime.now()
        current_datetime = datetime.strftime(current_date, "%Y-%m-%d ")
        for emp in self:
            total_ins_amount = 0
            for ins in emp.insurance:
                if ins.date_from <= current_datetime <= ins.date_to:
                    if ins.policy_coverage == 'monthly':
                        total_ins_amount += ins.amount * 12
                    else:
                        total_ins_amount += ins.amount
            deduced_amount_per_year = total_ins_amount - (
                        total_ins_amount * emp.insurance_percentage / 100)
            emp.deduced_amount_per_year = deduced_amount_per_year
            emp.deduced_amount_per_month = deduced_amount_per_year / 12
