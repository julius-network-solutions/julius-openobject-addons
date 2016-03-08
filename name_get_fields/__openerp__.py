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
    "name": "Name get fields (in context)",
    "summary": "Force the display name with context",
    "version": "0.1",
    "category": "Hidden",
    "description": """
Force in a special view the display name of a record
====================================================

How to use this:
----------------

    * put 'name_get_fields': ['name', 'field1','field2'] in your context.
    * inherit your model with 'name.get.inherited' \
(e.g. _inherit = ['sale.order', 'name.get.inherited'])
""",
    "author": "Julius Network Solutions",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "website": "http://www.julius.fr/",
    "images": [],
    "depends": [
                "base",
                ],
    "data": [],
    "demo": [],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
