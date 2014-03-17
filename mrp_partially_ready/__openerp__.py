# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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
    "name" : "MRP production partially ready to produce",
    "version" : "0.1",
    "author" : "Julius Network Solutions",
    "website" : "http://julius.fr",
    "category" : "Manufacturing",
    "depends" : [
        'mrp',
    ],
    "description": """
    This module will add a new state into the production order "Partially ready to produce".
    Example: You've got 1 product "Main product".
    This "Main product" is composed of 1 product "A" and 2 products "B".
    You need to produce 10 pieces of "Main product".
    By default the system will put the production order "Ready"
    when you have 10 products "A" and 20 products "B".
    
    Now with this module, the production order will be "Partially ready to produce"
    when you've got at least the quantity to produce 1 "Main product", ie 1 product "A" and 2 products "B"
    """,
    "demo" : [],
    "data" : [
        'mrp_view.xml',
    ],
    'installable' : True,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: