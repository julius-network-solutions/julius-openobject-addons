# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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
    'name': 'Tax certificate',
    'summary': 'Base for managing tax certificate',
    'version': '0.2',
    'category': 'Accounting & Finance',
	'description':"""
Tax certificate:
================

This module adds a tax certificate management.
""",
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr/',
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    'depends': [
        'analytic',
        'account',
    ],
    'data': [
        'data/tax_certificate_sequence.xml',
        'tax_certificate_view.xml',
        'wizard/create_tax_certificate_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
