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
    "name" : "Financial Discount",
    "summary": "Financial discount on sale orders",
    "version" : "0.3",
    "author" : "Julius Network Solutions",
    "website" : "http://julius.fr",
    "category" : "Sales Management",
    "depends" : [
        "sale",
        "stock",
    ],
    "description": """
Financial discount on a sale order
===============================
Module to manage a financial discount in sale orders

This module will add a field in the sale order, and it will work as the module "delivery" works.
    """,
    "demo" : [],
    "data" : [
        "sale_view.xml",
        "data/product_data.xml",
    ],
    'installable' : True,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: