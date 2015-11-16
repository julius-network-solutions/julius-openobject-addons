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
    "name": "Payment order generate move",
    "name": "Generate the account move on payment order validation",
    "version": "1.0",
    "author": "Julius Network Solutions",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "category": "Accounting & Finance",
    "depends": [
                "account",
                "account_payment",
                ],
    "demo":[],
    "data": [
             "account_journal_view.xml",
             "payment_export_view.xml",
             ],
    "description": """
Account move on payment order:
==============================

This module generate an account move on payment orders validation.
""",
    "active": False,
    "installable":True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
