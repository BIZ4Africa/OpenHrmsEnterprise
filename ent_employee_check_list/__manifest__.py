# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
{
    "name": "Enterprise Open HRMS Employee Checklist",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": """Manages Employee's Entry & Exit Process""",
    "description": """This module is used to remembering the employee's entry and exit progress.""",
    "author": "Cybrosys Techno Solutions, Open HRMS",
    "company": "Cybrosys Techno Solutions",
    "maintainer": "Cybrosys Techno Solutions",
    "website": "https://www.cybrosys.com",
    "depends": ["ent_employee_documents_expiry", "mail", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_activity_plan_template_data.xml",
        "data/mail_activity_plan_data.xml",
        "views/employee_check_list_views.xml",
        "views/hr_employee_documents_views.xml",
        "views/hr_employee_views.xml",
        "views/mail_activity_views.xml",
    ],
    "demo": ["demo/ent_employee_check_list_demo.xml"],
    "live_test_url": "https://www.youtube.com/watch?v=wtYRhGjhDKE&feature=youtu.be",
    "images": ["static/description/banner.jpg"],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": False,
}
