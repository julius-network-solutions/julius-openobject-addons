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

import openerp.tools
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class invoice_grouped_from_sale_order(orm.Model):
    _name = 'invoice.grouped.from.sale.order'
    
    def _make_invoice(self, cr, uid, partner, lines, context):
        partner_id = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        acc = partner_id.property_account_receivable.id
        if partner_id and partner_id.property_payment_term:
            pay_term = partner_id.property_payment_term[0]
        else:
            pay_term = False
        inv = {
            'name': 'Grouped invoice',
            'origin': 'Sale order to group',
            'type': 'out_invoice',
            'reference': "C%dVEGR"% partner ,
            'account_id': acc,
            'partner_id': partner,
            'invoice_line': [(6,0,lines)],
            'payment_term': pay_term,
            'user_id' : uid ,
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
        ids = context.get('active_ids')
        for o in so_obj.browse(cr,uid,ids):
            for line in o.order_line:
                lines.append(line.id)
        invoices_lines = self.pool.get('sale.order.line').invoice_line_create_cp(cr, uid, lines)

        for partner, val in invoices_lines.items():
            res = self._make_invoice(cr, uid, partner, val[1], context=context)
            invoice_ids.append(res)
            for so_id in val[0]:
                so_obj.write(cr, uid, [so_id], {
                    'state' : 'progress',
                    'invoice_ids': [(4, res)],
                }, context=context)
        return res

class sale_order_line(orm.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'


    def _get_line_qty_invoice(line):
        if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
            return line.product_uos_qty or line.product_uom_qty
        else:
            return self.pool.get('mrp.procurement').quantity_get(cr, uid, line.procurement_id.id, context)

    def invoice_line_create_cp(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_lines = {}
        invl_soll_map = {}
        parl_sol = {}
        for line in self.browse(cr, uid, ids, context):
            uosqty = self._get_line_qty(cr, uid,line)
            product = line.product_id.id or False
            price_unit = line.price_unit
            discount = line.discount
            partner = line.order_id.partner_id.id
            order = line.order_id.id

            parl_sol.setdefault(partner, list()).append(order)

            uos_id = (line.product_uos and line.product_uos.id) or False

            pkey = str(partner) + '-' +str(product) + '-' + str(price_unit) + '-' + str(discount)

            if product:
                inv_line = invoice_lines.get(pkey, False)
                if inv_line:
                    inv_line['quantity'] += uosqty
                    inv_line['note'] += '\n' + (line.notes or '')
                    invl_soll_map[pkey].append(line.id)
                else:
                    inv_line = {
                        'name': line.name ,
                        'price_unit': price_unit ,
                        'quantity': uosqty ,
                        'discount': discount ,
                        'uos_id': uos_id ,
                        'product_id': product ,
                        'invoice_line_tax_id': [(6,0,[x.id for x in line.tax_id])] ,
                    }
                    invoice_lines[pkey] = inv_line
                    invl_soll_map[pkey] = [line.id, ]
            else:
                inv_line = {
                    'name': line.name ,
                    'price_unit': price_unit ,
                    'quantity': uosqty ,
                    'discount': discount ,
                    'uos_id': uos_id ,
                    'product_id': product ,
                    'invoice_line_tax_id': [(6,0,[x.id for x in line.tax_id])] ,
                }
                invoice_lines[pkey] = inv_line
                invl_soll_map[pkey] = [line.id, ]

        invl_4part = {}

        for pkey, inv_line in invoice_lines.items():
            partner = int(pkey.split('-')[0])
            inv_id = self.pool.get('account.invoice.line').create(cr, uid, inv_line, context)
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
