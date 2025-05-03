# -*- coding: utf-8 -*-
###############################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Arjun S (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary
#    License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell
#    copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#    TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
{
    'name': 'Enterprise Open HRMS Legal Actions',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Managing Legal Actions""",
    'description': 'This module manages the legal actions of an employee.',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_lawsuit_views.xml',
    ],
    'demo': ['demo/ent_hr_lawsuit_management_demo.xml'],
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
