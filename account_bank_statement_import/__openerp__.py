# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
    "name": "Bank statement import",
    "summary": "Bank statement import with specific filters",
    "version": "1.2",
    "author": "Julius Network Solutions",
    "category": "Accounting & Finance",
    'images': [
        'images/1_accounting_config.jpeg',
        'images/2_filter_config.jpeg',
        'images/3_accounting_config.jpeg',
        'images/4_import_menu.jpeg',
        'images/5_import_pop_up.jpeg',
    ],
    "description": """
Import your bank statement files.
=================================

With this module you will be able to:
    * Set in your accounts configuration and other information by default
    * Add bank statements
    * View and change your bank statements

You will be able to define:
    * new parsers to import the files given by your bank.
""",
    "depends": [
        "account",
    ],
    "demo": [],
    "data": [
        "security/ir.model.access.csv",
        "data/filters_data.xml",
        "config_view.xml",
        "wizard/statement_import.xml",
    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

