# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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
    'name': 'UoM Merger',
    'version': '1.0',
    'category': 'Custom Module',
    'description': """

    This Module creates a wizard on:
    1. Select the UoM to merge, then which one to keep. All SO, PO, Invoices, Pickings, products, etc. of selected uom will be add to the one to keep.

    """,
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr',
    'depends': [
        'product',
    ],
    'data': [
        "wizard/uom_merger_view.xml", 
    ],
    'demo': [],
    'installable': False,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
