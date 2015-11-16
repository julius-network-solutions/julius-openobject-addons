# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
    "name": "Product index revision",
    "summary": "Generator of product index revison",
    "version": "0.1",
    "author": "Julius Network Solutions",
    "website": "http://julius.fr",
    "category": "Purchases Management",
    "depends": [
        "product",
        "mrp",
    ],
    "description": """
This module will give you the opportunity to:
=============================================

    * Duplicate simple products to manage index revisions, these revisions will have a start and end date
    * If a product got a BoM, the system will also duplicate the BoM (you will be able to manage if any change appears directly in the pop up)

This will also add:
-------------------
    * In sale view, you will only find revisions which are running in the current order date.
""",
    "demo": [],
    "data": [
        "wizard/add_plan_view.xml",
        "wizard/generator_view.xml",
        "product_view.xml",
    ],
    'installable': False,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
