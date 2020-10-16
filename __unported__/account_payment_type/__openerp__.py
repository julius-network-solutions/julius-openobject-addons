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
    "name": "Account Payment Type",
    "summary": "Manage type of payment (e.g. Checks, Credit cards, etc.)",
    "version": "0.1",
    "author": "Julius Network Solutions",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>, "
    "Lilian Olivier <lilian@julius.fr>",
    "website": "http://www.julius.fr",
    "category": "Accounting & Finance",
    "depends": [
                "account",
                ],
    "description": """
Payment types
=============

    * This module will a new model to manage type of payments
""",
    "demo": [],
    "data": [
             "security/ir.model.access.csv",
             "data/payment_type.xml",
             "views/payment_type.xml",
             "views/partner.xml",
             ],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
