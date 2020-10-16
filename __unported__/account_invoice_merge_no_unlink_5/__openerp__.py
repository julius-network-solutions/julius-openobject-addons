# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Syleam Info Services (<http://www.syleam.fr>) Claude Brulé.
#                  All Rights Reserved
#    $Id$
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
##############################################################################
#   TODO :
#       Verif if all invoices have the same price_list. Otherwise break !
#
##############################################################################

{
    "name": "Account invoice merge no unlink",
    "version": "0.2",
    "author": "Syleam , Julius Network Solutions",
    "website": "http://www.syleam.fr/ , http://www.julius.fr/",
    "category": "Generic Modules/Accounting",
    "description": """

Wizard to merge draft invoices.

""",
    "depends": [
        "base",
        "account",
        "sale",
    ],
    "data": [
        "workflow/workflow.xml",
        "wizard/invoice_merge_view.xml",
        "account_invoice_view.xml",
    ],
    "demo": ["data/account_demo.xml"],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
