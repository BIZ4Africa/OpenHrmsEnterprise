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
{
    "name": "Enterprise HR Company Policy",
    "version": "19.0.1.0.1",
    "category": "Generic Modules/Human Resources",
    "summary": "Manage and organize company policies within HR system",
    "description": """Manage company policies within the HR system.
    This module allows administrators to define company policies and display them on the 
    dashboard for easy employee access.""",
    "author": "Cybrosys Techno Solutions,Open HRMS",
    "company": "Cybrosys Techno Solutions",
    "maintainer": "Cybrosys Techno Solutions",
    "website": "https://www.openhrms.com",
    "depends": ["base", "ent_hrms_dashboard"],
    "data": [
        "security/res_company_policy_security.xml",
        "security/ir.model.access.csv",
        "views/res_company_policy_views.xml",
        "views/res_company_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ent_hr_company_policy/static/src/js/company_policy.js",
            "ent_hr_company_policy/static/src/css/company_policy.css",
            "ent_hr_company_policy/static/src/xml/dashboard_view.xml",
        ],
    },
    "images": ["static/description/banner.jpg"],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": False,
}
