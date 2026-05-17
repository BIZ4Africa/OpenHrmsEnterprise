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
from odoo import api, models


class ResUsers(models.Model):
    """ Inherit res users for adding fields """
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        """ This code is to create an employee while creating a user. """
        result = super(ResUsers, self).create(vals_list)
        for record in result:
            if record.share or record.employee_ids:
                continue
            self.env['hr.employee'].sudo().create({
                'name': record.name,
                'company_id': record.company_id.id or self.env.company.id,
                **self.env['hr.employee']._sync_user(record),
            })
        return result
