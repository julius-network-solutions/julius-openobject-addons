# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Inter Company Sale and Purchase",
    "version": "1.0",
    "depends": [
        "purchase",
        "sale",
    ],
    "author": "Julius Network Solutions",
    'images': [],
    "description": """
Inter Company Sale and Purchase module
====================================
This inter company sale and purchase module provides:
--------------------------------------------
    * Automatic creation of a purchase order when selling something to an partner linked to a system company.
    
    * Automatic creation of a sale order when purchasing something to an partner linked to a system company.
    
    """,
    "website": "http://julius.fr",
    "category": "Tools",
    "demo": [],
    "data": [
        "security/intercompany_security.xml",
        "purchase_view.xml",
        "sale_view.xml",
    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
