# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
    "name"      : "Account CODA extended - import bank statements from coda file or other",
    "version"   : "1.0",
    "author"    : "Julius Network Solutions",
    "category"  : "Account CODA",
    "description": """
    Module provides functionality to import
    bank statements from another files than coda with parser.
    """,
    "depends"   : [
       "account_voucher",
       "l10n_fr_coda",
    ],
    "demo_xml"  : [],
    "init_xml"  : [],
    "update_xml": [
        "wizard/account_coda_import.xml",
        "res_company_view.xml",
        "account_coda_view.xml",
        "security/ir.model.access.csv",
    ],
    "active"    : False,
    "installable" : True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

