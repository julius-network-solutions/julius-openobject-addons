# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Julius Network Solutions SARL <contact@julius.fr>
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Product Costs",
    "version": "0.1",
    "author": "Julius Network Solutions",
    "website": "http://julius.fr",
    "website": "Mathieu Vatel <mathieu@julius.fr>",
    "category": "Product management",
    "depends": [
                "product",
                "mrp",
                ],
    "description": """
Product Costs structure
=======================

Get all costs for a product:
----------------------------

    * Get prices from the BoM structure
    * Get prices from the BoM Routing
    * Get prices from fixes costs
    * etc.
""",
    "demo": [],
    "data": [
             "security/ir.model.access.csv",
             "views/product.xml",
             "views/product_costs.xml",
             ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
