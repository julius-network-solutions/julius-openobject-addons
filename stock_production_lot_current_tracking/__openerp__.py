# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions (<http://www.julius.fr/>) contact@julius.fr
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
    'name': 'Stock production lot current tracking',
    'version': '1.0',
    "category" : "Warehouse management",
	'description':"""
Production lot current Tracking module
====================================
This module will compute the current tracking of a stock production lot:
--------------------------------------------
    * By default the stock production lot location are defined just by moves
    * In this module, the current tracking is directly computed inside the record
    """,
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr/',
    'depends': [
        'stock',
    ],
    'data': [],
    'demo': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
