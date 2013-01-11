# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    
#    Copyright (c) 2011 Noviat nv/sa (www.noviat.be). All rights reserved.
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

from osv import osv, fields
import decimal_precision as dp
import netsvc
from tools.translate import _
logger=netsvc.Logger()

class account_coda(osv.osv):
    _name = 'account.coda'
    _description = 'Object to store CODA Data Files'
    _order = 'coda_creation_date desc'
    _columns = {
        'name': fields.char('CODA Filename',size=128, readonly=True),
        'coda_data': fields.binary('CODA File', readonly=True),
        'statement_ids': fields.one2many('coda.bank.statement','coda_id','Generated CODA Bank Statements', readonly=True),
        'note': fields.text('Import Log', readonly=True),
        'coda_creation_date': fields.date('CODA Creation Date', readonly=True, select=True),
        'date': fields.date('Import Date', readonly=True, select=True),
        'user_id': fields.many2one('res.users','User', readonly=True, select=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True)
    }
    _defaults = {
        'date': fields.date.context_today,
        'user_id': lambda self,cr,uid,context: uid,
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.coda', context=c),
    }        
#    _sql_constraints = [
#        ('coda_uniq', 'unique (name, coda_creation_date)', 'This CODA has already been imported !')
#    ]  

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({'coda_unlink': True})
        coda_st_obj = self.pool.get('coda.bank.statement')
        bank_st_obj = self.pool.get('account.bank.statement')
        for coda in self.browse(cr, uid, ids, context=context):
            for coda_statement in coda.statement_ids:                 
                if not context.get('coda_statement_unlink', False):
                    if coda_st_obj.exists(cr, uid, coda_statement.id, context=context):
                        coda_st_obj.unlink(cr, uid, [coda_statement.id], context=context)    
                if not context.get('bank_statement_unlink', False):
                    if coda_st_obj.exists(cr, uid, coda_statement.id, context=context) and (coda_statement.type == 'normal') and bank_st_obj.exists(cr, uid, coda_statement.statement_id.id, context=context):
                        bank_st_obj.unlink(cr, uid, [coda_statement.statement_id.id], context=context)                   
        context.update({'coda_unlink': False})
        return super(account_coda, self).unlink(cr, uid, ids, context=context)
  
account_coda()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
