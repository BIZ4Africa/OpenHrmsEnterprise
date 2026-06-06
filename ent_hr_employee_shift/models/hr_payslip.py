################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
import datetime
from datetime import datetime, timedelta

from odoo import _, api, fields, models, tools


class HrPayslip(models.Model):
    """Inherits the model hr.payslip to add extra functionalities"""
    _inherit = 'hr.payslip'

    def _get_worked_day_lines(self, domain=None, check_out_of_version=True):
        """
        Override to compute worked days from shift schedules instead of
        standard attendance.  Returns a list of dicts with keys expected
        by Odoo 19 hr.payslip.worked_days (work_entry_type_id + version_id).
        """
        def _work_entry_type(code):
            return self.env['hr.work.entry.type'].search(
                [('code', '=', code)], limit=1
            )

        def was_on_leave_interval(employee_id, date_from, date_to):
            date_from = fields.Datetime.to_string(date_from)
            date_to = fields.Datetime.to_string(date_to)
            return self.env['hr.leave'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('date_from', '<=', date_from),
                ('date_to', '>=', date_to)
            ], limit=1)

        res = []
        self.ensure_one()
        version = self.version_id
        if not version:
            return res

        work100_type = _work_entry_type('WORK100')

        interval_data = []
        for days in version.shift_schedule_ids:
            start_date = datetime.datetime.strptime(
                str(days.start_date), tools.DEFAULT_SERVER_DATE_FORMAT
            )
            nb_of_days = (days.end_date - days.start_date).days + 1
            for day in range(0, nb_of_days):
                working_intervals_on_day = days.hr_shift._get_day_work_intervals(
                    start_date + timedelta(days=day)
                )
                for interval in working_intervals_on_day:
                    interval_data.append(
                        (interval,
                         was_on_leave_interval(version.employee_id.id,
                                               interval[0],
                                               interval[1]))
                    )

        attendances = {
            'sequence': work100_type.sequence if work100_type else 1,
            'work_entry_type_id': work100_type.id if work100_type else False,
            'number_of_days': 0.0,
            'number_of_hours': 0.0,
        }
        leaves = {}

        for interval, holiday in interval_data:
            hours = (interval[1] - interval[0]).total_seconds() / 3600.0
            if holiday:
                leave_code = holiday.holiday_status_id.name
                if leave_code in leaves:
                    leaves[leave_code]['number_of_hours'] += hours
                else:
                    leaves[leave_code] = {
                        'sequence': 5,
                        'work_entry_type_id': holiday.holiday_status_id.id,
                        'number_of_days': 0.0,
                        'number_of_hours': hours,
                    }
            else:
                attendances['number_of_hours'] += hours

        uom_day = self.env.ref('product.product_uom_day', raise_if_not_found=False)
        uom_hour = self.env.ref('product.product_uom_hour', raise_if_not_found=False)

        for data in [attendances] + list(leaves.values()):
            data['number_of_days'] = (
                uom_hour._compute_quantity(data['number_of_hours'], uom_day)
                if uom_day and uom_hour
                else data['number_of_hours'] / 8.0
            )
            res.append(data)
        return res
