## -*- coding: utf-8 -*-
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
    "name" : "Purchase Report Aeroo",
    "version" : "0.1",
    "author" : "Julius Network Solutions",
    "website" : "http://www.julius.fr/",
    "category" : "Generic Modules/Others",
    "depends" : [
        "base",
        "purchase",
        "report_aeroo",
        "report_aeroo_ooo",
    ],
    "description" : """ Purchase report aeroo """,
    "init_xml" : [
        "report/purchase_report_view.xml",
    ],
    "demo_xml" : [],
    "update_xml" : [],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
