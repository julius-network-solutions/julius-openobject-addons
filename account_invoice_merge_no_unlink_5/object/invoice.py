# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#    Copyright (C) 2011 Zeekom ([http://www.Zeekom.fr/])
#              Damien CRIER [damien.crier@syleam.fr]
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc

class account_invoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'merged_invoice_id': fields.many2one('account.invoice',
                                            'Merged Invoice',
                                            readonly=True),
    }

    def __init__(self, pool, cr):
        if self._columns.get('state'):
            add_item = True
            for (a,b) in self._columns['state'].selection:
                if a == 'merged':
                    add_item = False
            if add_item:
                new_selection = []
                for (a,b) in self._columns['state'].selection:
                    if a == 'merged':
                        new_selection.extend([('merged', _('Merged'))])
                    new_selection.extend([(a,b)])
                self._columns['state'].selection = new_selection
        super(account_invoice, self).__init__(pool, cr)

    def merge_invoice(self, cr, uid, ids, merge_lines=False, journal_id=False, context=None):
        """ Merge draft invoices. Work only with same partner
            Moves all lines on the first invoice.
            @param merge_lines: sum quantities of invoice lines (or not)
            @type merge_line: boolean

            return account invoice id
        """
        if not context:
            context = {}
        if len(ids) <= 1:
            return False
        sql = "SELECT DISTINCT type, state, partner_id FROM account_invoice WHERE id IN (%s)" % ','.join(map(str, ids))
        cr.execute(sql)
        if len(cr.fetchall()) != 1:
            raise orm.except_orm(_('Invalid action !'),
                                 _('Can not merge invoice(s) on different partners or states !'))
        merged_inv_id = 0
        inv_line_obj = self.pool.get('account.invoice.line')
        default = {}
        if journal_id:
            default = {'journal_id': journal_id}
        for inv in self.browse(cr, uid, ids, context):
            if inv.state != 'draft':
                raise orm.except_orm(_('Invalid action !'), _('Can not merge invoice(s) that are already opened or paid !'))
            if merged_inv_id == 0:
                merged_inv_id = self.copy(cr, uid, inv.id, default=default, context=context)
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
                self.write(cr, uid, inv.id, {'merged_invoice_id': merged_inv_id}, context=context)
                self.write(cr, uid, merged_inv_id, {'origin': 'merged'}, context=context)
            else:
                line_ids = inv_line_obj.search(cr, uid, [('invoice_id','=',inv.id)])
                for inv_lin in inv_line_obj.browse(cr, uid, line_ids):
                    mrg_pdt_ids = inv_line_obj.search(cr, uid, [('invoice_id','=',merged_inv_id),('product_id','=',inv_lin.product_id.id)])
                    if merge_lines == True and mrg_pdt_ids:
                        qty = inv_line_obj._can_merge_quantity(cr, uid, mrg_pdt_ids[0], inv_lin.id)
                        if qty:
                            inv_line_obj.write(cr, uid, mrg_pdt_ids, {'quantity': qty})
                        else:
                            inv_line_obj.copy(cr, uid, inv_lin.id, {'invoice_id': merged_inv_id,})
                    else:
                        if merge_lines:
                            inv_line_obj.copy(cr, uid, inv_lin.id, {'invoice_id': merged_inv_id,})
                        else:
                            inv_line_obj.copy(cr, uid, inv_lin.id, {'invoice_id': merged_inv_id, 'origin': inv_lin.invoice_id.origin})
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
                self.write(cr, uid, [inv.id], {'merged_invoice_id': merged_inv_id}, context=context)
        if merged_inv_id:
            self.button_compute(cr, uid, [merged_inv_id])
        return merged_inv_id

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoices = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in invoices:
            if t['state'] in ('draft', 'cancel', 'merged'):
                unlink_ids.append(t['id'])
            else:
                raise orm.except_orm(_('Invalid action !'),
                                     _('Cannot delete invoice(s) that are already opened or paid !'))
        res = super(account_invoice, self).\
            unlink(cr, uid, unlink_ids, context=context)
        return res

class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    def _can_merge_quantity(self, cr, uid, id1, id2, context=None):
        """ Add quantity of invoice line if product_id,uos_id,account_id,discount,invoice_line_tax_id are same
            @param id1: invoice line ids for first invoice,
            @param id2: invoice line ids for second invoice,

            return quantity
        """
        qty = False
        invl1 = self.browse(cr, uid, id1)
        invl2 = self.browse(cr, uid, id2)
        if invl1.product_id.id and invl2.product_id.id and invl1.product_id.id == invl2.product_id.id \
            and invl1.price_unit == invl2.price_unit \
                and invl1.uos_id.id == invl2.uos_id.id \
                and invl1.account_id.id == invl2.account_id.id \
                and invl1.discount == invl2.discount\
                and invl1.invoice_line_tax_id == invl2.invoice_line_tax_id:
            qty = invl1.quantity + invl2.quantity
        return qty

    _columns = {
        'invoice_line_sale_id': fields.many2many(
            'sale.order.line',
            'sale_order_line_invoice_rel',
            'invoice_id', 'order_line_id',
            'Sale Order lines'),
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        if default == None:
            default = {}
        if context == None:
            context = {}
        line_ids = self.read(cr, uid, ids, ['invoice_line_sale_id'])['invoice_line_sale_id']

        default.update({'invoice_line_sale_id': [(6,0, line_ids)]})
        return super(account_invoice_line, self).\
            copy(cr, uid, ids, default=default, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
