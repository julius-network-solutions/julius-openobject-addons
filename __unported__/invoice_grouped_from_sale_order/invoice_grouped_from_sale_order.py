# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class invoice_grouped_from_sale_order(orm.Model):
    _name = 'invoice.grouped.from.sale.order'
    
    def _make_invoice(self, cr, uid, partner, lines, context):
        so_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.browse(cr, uid, partner, context=context)
        acc = partner_id.property_account_receivable.id
        ids = context.get('active_ids')
        group = []
        orders = so_obj.browse(cr, uid, ids, context=context)
        for order in orders:
            group.append(order.name)
        origin = ','.join(group)
        pay_term = partner_id and partner_id.property_payment_term and \
                partner_id.property_payment_term.id or False
        inv = {
            'name': _('Invoice Grouped'),
            'origin': origin,
            'type': 'out_invoice',
            'reference': "C%dVEGR"% partner,
            'account_id': acc,
            'partner_id': partner,
            'invoice_line': [(6, 0, lines)],
            'payment_term': pay_term,
            'user_id' : uid,
        }
        
        inv_obj = self.pool.get('account.invoice')
        inv_id = inv_obj.create(cr, uid, inv)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id

    def action_invoice_create_cp(self, cr, uid, ids, context=None):
        res = False
        invoices = {}
        invoice_ids = []
        if context is None:
            context = {}

        lines = []
        ids = []
        so_obj = self.pool.get('sale.order')
        so_line_obj = self.pool.get('sale.order.line')
        ids = context.get('active_ids')
        for o in so_obj.browse(cr,uid,ids):
            for line in o.order_line:
                lines.append(line.id)
        invoices_lines = so_line_obj.invoice_line_create_cp(cr,
                                        uid, lines, context=context)

        for partner, val in invoices_lines.items():
            res = self._make_invoice(cr, uid, partner, val[1], context=context)
            invoice_ids.append(res)
            for so_id in val[0]:
                so_obj.write(cr, uid, [so_id], {
                    'state' : 'progress',
                    'invoice_ids': [(4, res)],
                }, context=context)
                
        return self._open_invoices( cr, uid, ids, invoice_ids, context=context)           
                
    def _open_invoices(self, cr, uid, ids, invoice_ids, context=None):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
        tree_id = tree_res and tree_res[1] or False
        return {
            'name': _('Advance Invoice'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': invoice_ids[0],
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': "{'type': 'out_invoice'}",
            'type': 'ir.actions.act_window',
        }

class sale_order_line(orm.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    def invoice_line_create_cp(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_lines = {}
        invl_soll_map = {}
        parl_sol = {}
        procurement_obj = self.pool.get('mrp.procurement')
        inv_line_obj = self.pool.get('account.invoice.line')
        for line in self.browse(cr, uid, ids, context=context):
            uosqty = 0
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                uosqty = line.product_uos_qty or line.product_uom_qty
            else:
                uosqty = procurement_obj.quantity_get(cr, uid,
                            line.procurement_id.id, context=context)
            product = line.product_id.id or False
            price_unit = line.price_unit
            discount = line.discount
            partner = line.order_id.partner_id.id
            order = line.order_id.id

            parl_sol.setdefault(partner, list()).append(order)

            uos_id = (line.product_uos and line.product_uos.id) or False

            pkey = str(partner) + '-' + str(product) + '-' + str(price_unit) + '-' + str(discount)

            if product:
                inv_line = invoice_lines.get(pkey, False)
                if inv_line:
                    inv_line['quantity'] += uosqty
                    inv_line['note'] += '\n' + (line.notes or '')
                    invl_soll_map[pkey].append(line.id)
                else:
                    inv_line = {
                        'name': line.name,
                        'price_unit': price_unit,
                        'quantity': uosqty,
                        'discount': discount,
                        'uos_id': uos_id,
                        'product_id': product,
                        'invoice_line_tax_id': [(6,0,[x.id for x in line.tax_id])],
                    }
                    invoice_lines[pkey] = inv_line
                    invl_soll_map[pkey] = [line.id]
            else:
                inv_line = {
                    'name': line.name,
                    'price_unit': price_unit,
                    'quantity': uosqty,
                    'discount': discount,
                    'uos_id': uos_id,
                    'product_id': product,
                    'invoice_line_tax_id': [(6,0,[x.id for x in line.tax_id])],
                }
                invoice_lines[pkey] = inv_line
                invl_soll_map[pkey] = [line.id, ]

        invl_4part = {}

        for pkey, inv_line in invoice_lines.items():
            partner = int(pkey.split('-')[0])
            inv_id = inv_line_obj.create(cr, uid, inv_line, context)
            sol_ids = invl_soll_map[pkey]
            for sol_id in sol_ids:
                self.write(cr, uid, sol_id ,{
                            'invoice_id':[(4, inv_id)]
                            },context=context)
            self.write(cr, uid, sol_ids ,{
                        'invoiced':True
                        }, context=context)
            invl_4part.setdefault(partner, list()).append(inv_id)

        res = {}
        for kpar, vinv in invl_4part.items():
            res[kpar] = [ parl_sol[kpar] , vinv ]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
