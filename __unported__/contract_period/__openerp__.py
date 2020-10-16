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
    'name': 'Contract Period',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
Presentation:
=============

This module will adds a new object to be able to define how many days can be work / invoice during a month for a specific contract
or for all of them.
""",
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr',
    'contibutors': 'Mathieu Vatel <mathieu@julius.fr>',
    'depends': [
        'base',
        'account_analytic_analysis',
    ],
    'data': [
             'security/ir.model.access.csv',
             'contract_period_view.xml',
             'company_view.xml',
             ],
    'demo': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
