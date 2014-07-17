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
    "name": "Global Discount",
    "summary": "Global discount on sale orders",
    "version": "0.7",
    "author": "Julius Network Solutions",
    "website": "http://julius.fr",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "category": "Sales Management",
    "depends": [
        "sale",
        "invoice_link_sale",
    ],
    "description": """
Global discount on a sale order
===============================

Module to manage a global discount in sale orders.

This module will add a field in the sale order.
You will get the global discount in the invoice when you will invoice this order.
    """,
    "demo": [],
    "data": [
        "views/sale_view.xml",
        "views/report_quotation_discounted.xml",
        "data/product_data.xml",
    ],
    "test": [
        "test/sale_global_users.yml",
        "test/check_order_discounted.yml",
    ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: