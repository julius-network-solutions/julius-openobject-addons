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
    "version": "0.2",
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

Version 0.1:
------------

    * Simple management of the formula as sum.
    * The python method does not work.

Version 0.2:
------------

    * Add the possibility to choose what kind of formula to use (sum, multiplication, etc.).
    * Add the possibility to get a value from a linked field.
    * Add the possibility to get a value from a python computation.
    * Add an action to recompute only values (e.g. : use it when you change fixed prices).
""",
    "demo": [],
    "data": [
             "security/ir.model.access.csv",
             "views/product.xml",
             "views/product_costs.xml",
             "views/mrp_bom.xml",
             ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
