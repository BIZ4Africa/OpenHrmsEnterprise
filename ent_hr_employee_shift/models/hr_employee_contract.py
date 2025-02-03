# -*- coding: utf-8 -*-
################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE,ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrContract(models.Model):
    """This is used to inherit hr contract to add additional fields"""
    _inherit = 'hr.contract'

    shift_schedule_ids = fields.One2many('hr.shift.schedule',
                                         'rel_hr_schedule_id',
                                         string="Shift Schedule",
                                         help="Shift schedule")
    working_hours_id = fields.Many2one('resource.calendar',
                                       string='Working Schedule',
                                       help="Working hours")
    department_id = fields.Many2one('hr.department',
                                    string="Department",
                                    help="Department",
                                    required=True)


class HrShiftSchedule(models.Model):
    """This is used to inherit hr.shift.schedule to add additional fields and
    functionalities"""
    _name = 'hr.shift.schedule'
    _description = 'To schedule the shift'

    start_date = fields.Date(string="Date From",
                             required=True,
                             help="Starting date for the shift")
    end_date = fields.Date(string="Date To",
                           required=True,
                           help="Ending date for the shift")
    rel_hr_schedule_id = fields.Many2one('hr.contract',
                                         string="Relational Field")
    hr_shift_id = fields.Many2one('resource.calendar',
                                  string="Shift",
                                  required=True,
                                  help="Shift")
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 help="Company")

    @api.onchange('start_date', 'end_date')
    def onchange_get_department(self):
        """Adding domain to  the hr_shift field"""
        hr_department = None
        if self.start_date:
            hr_department = self.rel_hr_schedule_id.department_id.id

        return {
            'domain': {
                'hr_shift_id': [('hr_department_id', '=', hr_department)]
            }
        }

    @api.model
    def create(self, vals):
        self._check_overlap(vals)
        return super().create(vals)

    def write(self, vals):
        self._check_overlap(vals)
        return super().write(vals)

    def _check_overlap(self, vals):
        """This is used to check the overlap"""
        if self:
            shifts = self.env['hr.shift.schedule']. \
                search([('rel_hr_schedule_id', '=', self.rel_hr_schedule.id)])
            shifts -= self
        else:
            shifts = self.env['hr.shift.schedule']. \
                search(
                [('rel_hr_schedule_id', '=', vals.get('rel_hr_schedule_id'))])
        start_date = fields.Date.to_date(vals.get('start_date', False)) if vals \
            .get('start_date', False) else self.start_date
        end_date = fields.Date.to_date(vals.get('end_date', False)) if vals \
            .get('end_date', False) else self.end_date
        if start_date and end_date:
            for each in shifts:
                if each.start_date <= start_date <= each.end_date \
                        or each.start_date <= end_date <= each.end_date \
                        or each.start_date <= start_date \
                        and each.end_date >= end_date \
                        or each.start_date >= start_date \
                        and each.end_date <= end_date:
                    raise UserError(_('The dates may not overlap with one '
                                      'another.'))
            if start_date > end_date:
                raise UserError(_('Start date should be less than end date in '
                                  'shift schedule.'))
        return True
