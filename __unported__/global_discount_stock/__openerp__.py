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
    "name": "Global Discount with stock",
    "summary": "Global discount on sale orders when stock has been installed",
    "version": "0.1",
    "author": "Julius Network Solutions",
    "website": "http://julius.fr",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "category": "Sales Management",
    "depends": [
        "stock",
        "global_discount",
        "invoice_link_sale",
    ],
    "description": """
Global discount on a sale order
===============================
Module to manage a global discount in sale orders

This module will be installed automatically when stock and global_discount
have been installed.
This will work as the module "delivery" works.
    """,
    "demo": [],
    "data": [],
    'installable': True,
    'auto_install': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
