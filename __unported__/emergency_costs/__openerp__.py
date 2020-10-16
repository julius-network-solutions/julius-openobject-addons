# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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
    "name": "Emergency Costs",
    "summary": "Manage emergency costs in sale orders",
    "version": "0.5",
    "author": "Julius Network Solutions",
    "website": "http://julius.fr",
    "category": "Sales Management",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "depends": [
                "base_added_costs",
                ],
    "description": """
Emergency Costs in sale orders
==============================

How this is working ?
---------------------

You will find a new field in the sale order line : Emergency Costs.

Once the you've created an invoice for this order, you will be able to generate
a line of emergency costs if needed by clicking on the
"Generate Emergency Costs" in the invoice. 
""",
    "demo": [],
    "data": [
             "data/product_data.xml",
             "views/sale.xml",
             "views/invoice.xml",
             ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: