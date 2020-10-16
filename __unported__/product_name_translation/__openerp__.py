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
    "name" : "Product Name Translation",
    "version" : "0.1",
    "author" : "Julius Network Solutions",
    "website" : "www.julius.fr",
    "category" : "Sales Management",
    "depends" : [
        "base",
        "product",
    ],
    "description" : """ The product name is posted in several languages """,
    "demo" : [],
    "data" : [
        "wizard/change_product_name.xml",  
        "product_name.xml",
    ],
    "installable": False,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
