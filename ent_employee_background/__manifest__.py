################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Arjun S (odoo@cybrosys.com)
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
    "name": "Enterprise HRMS Employee Background Verification",
    "version": "1.0.1",
    "category": "Human Resources",
    "summary": """Verify the background details of an Employee """,
    "author": "Cybrosys Techno Solutions, Open HRMS",
    "company": "Cybrosys Techno Solutions",
    "maintainer": "Cybrosys Techno Solutions",
    "website": "https://www.cybrosys.com",
    "depends": [
        "mail",
        "ent_hr_employee_updation",
        "contacts",
        "portal",
        "website",
    ],
    "data": [
        "data/mail_template_data.xml",
        "views/employee_verification_views.xml",
        "views/res_partner_views.xml",
        "views/agent_portal_templates.xml",
    ],
    "demo": ["demo/ent_employee_background_demo.xml"],
    "images": ["static/description/banner.jpg"],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": False,
}
