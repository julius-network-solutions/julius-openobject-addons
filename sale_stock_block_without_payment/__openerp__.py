# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    Copyright (C) 2015: Ursa Information Systems
#    Author: Sandip Mangukiya (<smangukiya@ursainfosystems.com>)
#    Website:(<http://www.ursainfosystems.com>).
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
    'name': 'Block delivery if invoice is due',
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': [
        'Ursa Information Systems',
        'Julius Network Solutions'
    ],
    'category': 'Sale Management',
    'depends': [
        'sale_stock',
        'account_accountant'
    ],
    'data': [
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/account_payment_term.xml',
    ],
    'installable': True,
    'active': True,
}
