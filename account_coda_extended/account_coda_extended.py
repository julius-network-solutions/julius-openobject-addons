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

import time

from osv import osv,fields
from tools.translate import _
     
class account_bankimport_filters(osv.osv):
    _name = "account.bankimport.filters"
    _description = "Define the filters, which is related to the file"
    _columns = {
        'filter' : fields.char('Filtername', size=64, required=True),
        'name' : fields.char('Filename', size=128, required=True),
    }
account_bankimport_filters()

# Save data for each company
class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'bank_journalid' :  fields.many2one('account.journal', 'Bank Journal'),
        'def_payable' :  fields.many2one('account.account', 'Default Payable Account', domain=[('type','=','payable')]),
        'def_receivable' :  fields.many2one('account.account', 'Default Receivable Account', domain=[('type','=','receivable')]),
        'filter_id': fields.many2one('account.bankimport.filters', 'Filter'),
    }
res_company()

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'
    _columns = {
        'coda_id': fields.many2one('account.coda','CODA'),
    }
account_bank_statement()

class account_coda(osv.osv):
    _inherit = 'account.coda'
    _columns = {
        'bank_statement_ids': fields.one2many('account.bank.statement','coda_id','Generated CODA Bank Statements', readonly=True),
    }
account_coda()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: