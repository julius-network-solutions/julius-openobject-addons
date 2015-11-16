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
    "name" : "Sale stock without auto procurement",
    "version" : "0.1",
    "author" : "Julius Network Solutions",
    "website" : "http://julius.fr",
    "category" : "Warehouse Management",
    "depends" : [
        'sale',
        'sale_stock',
        "stock_special_location",
    ],
    "description": """
    This module will check if the move is due to a specific location.
    If this is a special location, then the sale_order will create the picking as usual, but not the associated procurement.
    The procurement will be generated with an action checking the need by date, and create automatically the procurement needs.
    """,
    "demo" : [],
    "data" : [
#        "sale_view.xml",
    ],
    'installable' : False,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
