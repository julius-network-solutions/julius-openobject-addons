# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class create_invoice(orm.TransientModel):
    _name = "create.invoice"
    _description = "Create invoice"
    
    def open_invoices(self, cr, uid, ids,
                      invoice_id, type='out_invoice', context=None):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.pool.get('ir.model.data')
        account_invoice_obj = self.pool.get('account.invoice')
        if type == 'out_invoice':
            form_res = ir_model_data.\
                get_object_reference(cr, uid,
                                     'account',
                                     'invoice_form')
        if type == 'in_invoice':
            form_res = ir_model_data.\
                get_object_reference(cr, uid,
                                     'account',
                                     'invoice_supplier_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.\
            get_object_reference(cr, uid,
                                 'account',
                                 'invoice_tree')
        tree_id = tree_res and tree_res[1] or False
        return {
            'name': _('Advance Invoice'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': invoice_id,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': {'type': type},
            'type': 'ir.actions.act_window',
        }
    
    def _generate_invoice(self, cr, uid, ids,
                          type='out_invoice', context=None):
        contract_obj = self.pool.get('account.analytic.account')
        if context is None:
            context = {}
        active_id = context.get('active_id')
        contract_data = contract_obj.\
            browse(cr, uid, active_id, context=context)
        partner_id = context.get('partner_id') or \
            contract_data.partner_id.id
        company_id = context.get('company_id') or \
            contract_data.company_id.id
        account_invoice_obj = self.pool.get('account.invoice')
        values = account_invoice_obj.\
            onchange_partner_id(cr, uid, ids, type, partner_id)
        account_id = values['value']['account_id']
        new_id = account_invoice_obj.create(cr, uid, {
                'type': type,
                'contract_id': active_id,
                'partner_id': partner_id,
                'company_id': company_id,
                'account_id': account_id,
                'payment_term': contract_data.payment_term_id.id,        
            },context=context)
        return self.open_invoices(cr, uid, ids,
                                  new_id, type=type, context=context)
    
    def customer_invoice(self, cr, uid, ids, context=None):
        return self._generate_invoice(cr, uid, ids,
                                      'out_invoice', context=context)
    
    def supplier_invoice(self, cr, uid, ids, context=None):
        return self._generate_invoice(cr, uid, ids,
                                      'in_invoice', context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
