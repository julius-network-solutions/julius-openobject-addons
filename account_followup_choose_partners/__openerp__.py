# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Payment Follow-up Management',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
This module will adds a step to send the letters and mails to the customers.

""",
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr',
    'images': [],
    'depends': ['account_followup'],
    'data': [
#        'security/ir.model.access.csv',
        'wizard/account_followup_print_view.xml',
    ],
    'demo': ['account_followup_demo.xml'],
    'test': [
        'test/account_followup.yml',
        #TODO 'test/account_followup_report.yml', --> Need to wait for second step in order to check report (expects after first)
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
