# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
###############################################################################

{
    "name": "Inter Company Invoice",
    "version": "1.0",
    "depends": [
        "account",
    ],
    "author": "Julius Network Solutions",
    "contributor" : "Yvan Patry <yvan@julius.fr>",
    'images': [],
    "description": """
Inter Company Invoice module
====================================

This inter company invoice module provides:
--------------------------------------------

    * Automatic creation of a supplier invoice when invoicing a customer linked to a system company.
""",
    "website": "http://julius.fr",
    "category": "Accounting & Finance",
    "demo": [],
    "data": [
        "security/intercompany_security.xml",
        "account_view.xml",
    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
