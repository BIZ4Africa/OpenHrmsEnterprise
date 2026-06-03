######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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


class ResCompany(models.Model):
    """Extend res.company to store company policy information."""
    _inherit = 'res.company'

    company_info = fields.Html(string="Company Policy",
                               help="Defines the company policy to be displayed to users.")


class ResCompanyPolicy(models.TransientModel):
    """Transient model used to display company policy information."""
    _name = 'res.company.policy'
    _description = 'Company Policy'

    company_id = fields.Many2one('res.company', string="Company",
                             help="Company of the policy",
                             default=lambda self: self.env.company)
    policy_info = fields.Html(string="Policy Info",
                              related='company_id.company_info')
