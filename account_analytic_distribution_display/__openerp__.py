# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
    "name": "Display a menu for Analytic distribution",
    "summary": "Add filter to display all fields on analytic line list",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """
Analytic lines tree view display
================================
This module adds a menu for distribution.
    """,
    "author": "Julius Network Solutions",
    "website": "http://www.julius.fr",
    "depends": [
        "account_analytic_plans",
    ],
    "data": [
        "account_analytic_distribution_view.xml",
    ],
    "demo": [],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
