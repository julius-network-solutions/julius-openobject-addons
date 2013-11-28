# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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

from osv import fields, osv
from tools.translate import _

class account_invoice_merge(osv.osv_memory):
    
    _name = 'account.invoice.merge'
    
    _columns = {
        'grouped' : fields.boolean('Sum quantity of lines'),
        'journal_id' : fields.many2one('account.journal', 'Journal'),
    }
    
    def _openForm(self, cr, uid, domain, context=None):
        """
            Invoice is merge then Open the merge Invoice in tree view.
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj =  self.pool.get('ir.actions.act_window')
        inv_obj = self.pool.get('account.invoice')
        type = inv_obj.browse(cr, uid, context.get('active_id'), context=context).type
        if type == 'in_invoice':
            xml_id = 'action_invoice_tree2'
        if type == 'out_invoice':
            xml_id = 'action_invoice_tree1'
        result = mod_obj._get_id(cr, uid, 'account', xml_id)
        id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
        result = act_obj.read(cr, uid, id, context=context)
        result['domain'] = domain
        return result
    
    def mergeInvoices(self, cr, uid, ids, context=None):
        """
            Call the merge_invoice method of account.invoice object and pass the related parameter.
        """
        if not context:
            context = {}
        inv_obj = self.pool.get('account.invoice')
        current = self.browse(cr, uid, ids[0], context=context)
        invoice_ids = context.get('active_ids') or []
        new_invoice = inv_obj.merge_invoice(cr, uid, invoice_ids, current.grouped, current.journal_id and current.journal_id.id or False, context=context)
        return self._openForm(cr, uid, "[('id','=', "+ str(new_invoice)  +")]",context)
    
account_invoice_merge()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

