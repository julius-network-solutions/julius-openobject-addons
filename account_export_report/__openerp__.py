# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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
    "name" : "Account Export Report",
    "version" : "0.1",
    "author" : "Julius Network Solutions",
    'images': ['images/export.jpeg', 'images/menu.jpeg'],
    "website" : "www.julius.fr",
    "category" : "Generic Modules/Others",
    "depends" : [
        "base",
        "account",
        "report_aeroo",
        "report_aeroo_ooo",
    ],
    "description" : """ 
Export Account Report
---------------------
*Interface easy to use

You have access to a window that allows you to filter the accounting information you want to analyze via a new menu.

*Choose the informations to export

This module provides:

You can also choose whether you want to export the account children informations.

The ability to export the accounting lines records with all the relevant analytical informations and return an ODS file (Use with Excel, OpenOffice)

""",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "report/account_export_aeroo_view.xml",
        "wizard/account_export_report.xml",
    ],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
