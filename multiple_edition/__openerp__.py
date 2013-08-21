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
    "name": 'Multiple Edition',
    "version": '1.0',
    "description": """ 
This module give the possibility to edit several record of a table.

Just check the list of product that requires modification, then choose multiple edition on "more" menu.

CHoose the field type and the value.

Suitable for all objects, you only have to define the objects for which you want to add this option in the configuration part of OpenERP.  
""",
    "author": 'Julius Network Solutions',
    'images': ['images/wizard.jpeg', 'images/product.jpeg', 'images/multi.jpeg'],
    "website": 'http://www.julius.fr/',
    "depends": [
        'base',
        'product',
    ],
    "init_xml": [],
    "update_xml": [
        "multiple_edition_view.xml",
        "res_config_view.xml",
    ],
    "demo_xml": [],
    "installable": True,
    "active": False,
    "category" : "Base extra Modules",
    "test": [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
