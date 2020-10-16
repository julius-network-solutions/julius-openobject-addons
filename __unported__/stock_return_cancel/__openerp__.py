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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    "name": "Stock return cancel",
    "summary": "Add type of return in return wizard to "
    "be able to work as invoices",
    "version": "0.2",
    "author": "Julius Network Solutions",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "website": "http://julius.fr",
    "category": "Warehouse Management",
    "depends": [
                "stock",
                ],
    "description": """
Return pickings as invoices:
============================

This module will add an option in picking return wizard to be able to work
like the refund process of invoices works
""",
    "demo": [],
    "data": [
             "wizard/stock_return_picking_cancel.xml",
             ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: