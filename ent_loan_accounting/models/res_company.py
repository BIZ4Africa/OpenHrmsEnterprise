# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
from odoo import fields, models


class ResCompany(models.Model):
    """Loan disbursement settings, per company.

    A loan is expressed in its own currency (the employee contract currency),
    the company books are kept in the company currency. These two settings
    decide how the disbursement entry bridges the two, so that the decision
    stays a configuration choice and not a code change:

    * ``ent_loan_currency_conversion`` — post the entry in the company currency
      at the rate of the entry date (recommended), or keep the legacy raw
      posting;
    * ``ent_loan_conversion_date`` — which date the entry (and its rate) uses.
    """
    _inherit = 'res.company'

    ent_loan_currency_conversion = fields.Boolean(
        string="Convert the loan disbursement to the company currency",
        default=True,
        help="When the loan is expressed in a currency other than the company "
             "currency (a CDF loan in a USD company, for instance), the "
             "disbursement entry is converted at the rate of the entry date "
             "and carries the loan currency — exactly like the payslip entry "
             "that recovers the installments. Disable only to reproduce the "
             "legacy behaviour (raw amount posted in the company currency).")
    ent_loan_conversion_date = fields.Selection(
        selection=[
            ('move_date', 'Accounting entry date (approval day)'),
            ('loan_date', 'Loan date'),
            ('payment_date', 'First installment date'),
        ],
        string="Loan disbursement entry date",
        default='move_date',
        required=True,
        help="Date carried by the loan disbursement entry, and therefore the "
             "date of the currency rate applied to it.")
