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
from odoo import api, fields, models


class HrLawsuit(models.Model):
    _name = 'hr.lawsuit'
    _description = 'Hr Lawsuit Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, vals):
        """Create a new sequence"""
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.lawsuit')
        return super(HrLawsuit, self).create(vals)

    def won(self):
        self.state = 'won'

    def cancel(self):
        self.state = 'cancel'

    def loss(self):
        self.state = 'fail'

    def process(self):
        self.state = 'running'

    @api.depends('party2', 'employee_id')
    def _compute_party2_name(self):
        """Compute the name of the second party name"""
        for each in self:
            if each.party2 == 'employee':
                each.party2_name = each.employee_id.name

    name = fields.Char(string='Code', copy=False)
    ref_no = fields.Char(string="Reference Number")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company,
                                 help='Name of the company of the user')
    requested_date = fields.Date(string='Date', copy=False,
                                 help='Start Date')
    hearing_date = fields.Date(string='Hearing Date',
                               help='Upcoming hearing date')
    court_name = fields.Char(string='Court Name', track_visibility='always',
                             states={'won': [('readonly', True)]},
                             help='Name of the Court')
    judge = fields.Char(string='Judge', track_visibility='always',
                        states={'won': [('readonly', True)]},
                        help='Name of the Judge')
    lawyer_id = fields.Many2one('res.partner', string='Lawyer',
                             track_visibility='always',
                             help='Choose the contact of Layer from the '
                                  'contact list',
                             states={'won': [('readonly', True)]})
    first_party_id = fields.Many2one('res.company', string='First Party',
                             required=1,
                             default=lambda self: self.env.company,
                             help='Choose the company as first Party',)
    party2 = fields.Selection([('employee', 'Employee'),
                               ('partner', 'Partner'),
                               ('other', 'Others')], default='employee',
                              string='Second Party', required=1,
                              help='Choose the second party in the legal '
                                   'issue.It can be Employee, Contacts or '
                                   'others.', )
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  copy=False,
                                  help='Choose the Employee')
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 copy=False,
                                 help='Choose the partner')
    other_name = fields.Char(string='Name', help='Enter the details of other '
                                                 'type')
    party2_name = fields.Char(compute='_compute_party2_name', string='Name',
                              store=True)
    case_details = fields.Html(string='Case Details', copy=False,
                               track_visibility='always',
                               help='More details of the case')
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('cancel', 'Cancelled'),
                              ('fail', 'Failed'),
                              ('won', 'Won')], string='Status',
                             default='draft', track_visibility='always',
                             copy=False,
                             help='Status')
