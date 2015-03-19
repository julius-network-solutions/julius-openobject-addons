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
    'name': 'Image on sale order lines',
    'version': '0.2',
    'category': 'Base',
    'description': """
Image on sale order line
========================

""",
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr/',
    'images': [],
    'depends': [
        'sale_layout',
        'sale_order_line_image',
    ],
    'data': [
        'views/report_quotation.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
