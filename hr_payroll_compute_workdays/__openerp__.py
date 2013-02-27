# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

{
    'name': 'Payroll compute worked days',
    'version': '1.0',
    'category': 'Human Resources',
    "author" : "Julius Network Solutions",
    "website" : "http://www.julius.fr/",
    "depends" : [
        "hr_payroll",
    ],
    "description": """
    This module gives you the opportunity to recompute as you which the Worked days by inheriting the method "compute_worked_days"
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
#        "security/ir.model.access.csv",
    ],
    'installable' : True,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
