# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrGratuityAccountingConfiguration(models.Model):
    """Model to record different gratuity configuration"""
    _name = 'hr.gratuity.accounting.configuration'
    _description = "Gratuity Accounting Configuration"

    name = fields.Char(string='Name', help='Name of Gratuity Accounting')
    active = fields.Boolean(default=True, string='Active', help='Is Active')
    gratuity_start_date = fields.Date(string='Start Date',
                                      help="Starting date of the gratuity")
    gratuity_end_date = fields.Date(string='End Date',
                                    help="Ending date of the gratuity")
    gratuity_credit_account_id = fields.Many2one('account.account',
                                                 string="Gratuity credit account",
                                                 help="Credit account for the"
                                                      " gratuity")
    gratuity_debit_account_id = fields.Many2one('account.account',
                                                string="Gratuity debit account",
                                                help="Debit account for the "
                                                     "gratuity")
    gratuity_journal_id = fields.Many2one('account.journal',
                                          string="Gratuity Journal",
                                          help="Journal for the gratuity")
    config_contract_type = fields.Selection(
        [('limited', 'Limited'),
         ('unlimited', 'Unlimited')], default="limited", required=True,
        string='Contract Type')
    gratuity_configuration_table_ids = fields.One2many('gratuity.configuration',
                                                       'gratuity_accounting_configuration_id',
                                                       string="Gratuity configuration table",
                                                       help="Gratuity configuration table")

    @api.onchange('gratuity_start_date', 'gratuity_end_date')
    def _onchange_date(self):
        """ Function to check date """
        if self.gratuity_start_date and self.gratuity_end_date:
            if not self.gratuity_start_date < self.gratuity_end_date:
                raise UserError(_("Invalid date configuration!"))

    _sql_constraints = [('name_uniq', 'unique(name)',
                         'Gratuity configuration name should be unique!')]
