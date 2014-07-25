# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    "name": "HR Employee product automatic",
    "summary": "Create a product for the employee",
    "version": "0.2",
    "author": "Julius Network Solutions",
    "website": "http://www.julius.fr/",
    "category": "Human Resources",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "depends": [
        'hr',
        'hr_timesheet',
        'hr_employee_header',
    ],
    "description": """
Automatic user for products
===========================

This module adds a button inside the employee form to create a product for each
employee to be able to invoice the analytic lines with the good associated
product.
""",
    "demo": [],
    "data": [
        'data/category_data.xml',
        'product_view.xml',
        'employee_view.xml',
    ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
