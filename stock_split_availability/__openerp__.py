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
    "name" : "Stock split availability",
    "version" : "1.1",
    "author" : "Julius Network Solutions",
    "category": "Warehouse Management",
    "description" : """
    This module will allow to split moves when there are some moves which are partially available.
    E.g.: You have to send 10 PCE, but right now you only got 8 PCE ready.
    By default OpenERP will tells you that this move is not ready when you will check the availability of this move.
    
    This module will split the move into 2 moves:
        - One of 8 PCE ready.
        - One of 2 PCE not ready.
    
    Then when you will check the availability again in this Picking, and the 2 last PCE are ready and the 8 PCE not send yet,
    This will merge these to move into only one.
    
    """,
    "website" : "http://www.julius.fr",
    "depends" : [
         "stock",
         'product',
    ],
    "data" : [
        "stock_view.xml",
    ],
    "demo" : [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
