# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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
    'name': 'Customer & Supplier Relationship Management',
    'version': '1.0',
    'category': 'Generic Modules/CRM & SRM',
    'description': """ This modules adds the State of Mind into the crm phonecall missing in V6 """,
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr',
    'depends': [
        'crm',
    ],
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'crm_phonecall_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
