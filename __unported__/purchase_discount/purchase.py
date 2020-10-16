# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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
import openerp.addons.decimal_precision as dp

class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _amount_all_discount(self, cr, uid, ids,
                             field_name, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
               val1 += line.price_subtotal
               price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
               for c in self.pool.get('account.tax').\
                   compute_all(cr, uid, line.taxes_id, price, line.product_qty,
                               line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            amount_tax = cur_obj.round(cr, uid, cur, val)
            amount_untaxed = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_tax'] = amount_tax
            res[order.id]['amount_untaxed'] = amount_untaxed
            res[order.id]['amount_total'] = amount_tax + amount_untaxed
        return res

    def _get_order_discount(self, cr, uid, ids, context=None):
        result = {}
        line_obj = self.pool.get('purchase.order.line')
        for line in line_obj.browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = { 
        'amount_untaxed': fields.function(_amount_all_discount,
            digits_compute=dp.get_precision('Account'),
            string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order_discount, None, 10),
            }, multi="sums", help="The amount without tax",
            track_visibility='always'),
        'amount_tax': fields.function(_amount_all_discount,
            digits_compute=dp.get_precision('Account'),
            string='Taxes',
            store={
                'purchase.order.line': (_get_order_discount, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all_discount,
            digits_compute=dp.get_precision('Account'),
            string='Total',
            store={
                'purchase.order.line': (_get_order_discount, None, 10),
            }, multi="sums",help="The total amount"),
    }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(purchase_order, self).\
            _prepare_inv_line(cr, uid, account_id=account_id,
                              order_line=order_line,context=None)
        if order_line:
            res['discount'] = order_line.discount or 0.00
        return res

class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    def _amount_line_discount(self, cr, uid, ids,
                              field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, price,
                                        line.product_qty, line.product_id,
                                        line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'discount': fields.float('Discount (%)',
            digits_compute=dp.get_precision('Discount')),
        'price_subtotal': fields.function(_amount_line_discount,
            string='Subtotal', digits_compute= dp.get_precision('Account')),
    }

    _defaults = {
        'discount': 0.0,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
