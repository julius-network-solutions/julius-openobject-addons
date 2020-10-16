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
    "name": "Picking list from partner",
    "summary": "Get a list of picking for a partner on a wanted period",
    "version": "0.2",
    "author": "Julius Network Solutions",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "website": "http://julius.fr",
    "category": "Warehouse Management",
    "depends": [
                "stock",
                ],
    "description": """
Picking list from the partner form
==================================

This module will add a button into the partner form.
Clicking on it will open a pop up where you will have to choose 2 dates.
Then you will have the list of pickings for this partner during
the chosen period. 

You will also find a new menuitem in the warehouse menu.
""",
    "demo": [],
    "data": [
             "wizard/open_picking_list.xml",
             "views/partner.xml",
             "views/stock.xml",
             ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: