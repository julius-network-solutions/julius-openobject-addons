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
    "name" : "Product Partner code on sale",
    "version" : "1.0",
    "author" : "Julius Network Solutions",
    "website" : "http://julius.fr",
    "category" : "Sales Management",
    "depends" : [
        'base',
        'product',
        'sale',
        'product_partner_code',
    ],
    "description": """
    Add a new object which allow to define partner codes
    for products and to display it on sale order lines
    """,
    "demo" : [],
    "data" : [
        'sale_view.xml',
    ],
    'installable' : False,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
