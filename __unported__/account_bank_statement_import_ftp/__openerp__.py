# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Julius Network Solutions SARL <contact@julius.fr>
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
    "name": "Bank statement import ftp",
    "summary": "Bank statement import with specific filters ftp",
    "version": "1.3",
    "author": "Julius Network Solutions",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "category": "Accounting & Finance",
    "description": """
Import your bank statement files automatically.
===============================================

    * Define your folders to import
    * Define the parser to use
    * This will automatically import them in your system

""",
    "depends": [
                "account_bank_statement_import",
                ],
    "demo": [],
    "data": [
             'security/ir.model.access.csv',
             'cron_import_statement.xml',
             'bank_statement_view.xml',
             ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

