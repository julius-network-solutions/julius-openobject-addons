# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions (<http://www.julius.fr/>) contact@julius.fr
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
    'name': 'Stock picking complete',
    'version': '1.0',
    "category" : "Warehouse management",
	'description':"""
    This module adds a boolean field which checks if the picking is complete or not
    """,
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr/',
    'depends': [
        'stock',
    ],
    'data': [
        'stock_view.xml',
    ],
    'demo': [],
    'installable': True,
    'active': False,
    'license': 'GPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
