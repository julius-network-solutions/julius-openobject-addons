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
import openerp.addons.decimal_precision as dp

class purchase_order(orm.Model):
    _inherit = "purchase.order"
    
    def _check_if_ecotax(self, cr, uid, line, context=None):
        if context is None:
            context = {}
        if not line.product_id or \
            (not line.product_id.ecotax_type in ['1','2'] and \
             not line.product_id.categ_id.ecotax_type in ['1','2'])and \
             not line.order_id.partner_id.country_id.subject_to_ecotax is True:
            return False
        return True
    
    def generate_ecotax_line(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('purchase.order.line')
        for purchase in self.browse(cr, uid, ids, context=context):
            product_list = {}
            if purchase.state != 'draft':
                continue
            for line in purchase.order_line:
                if not self._check_if_ecotax(cr, uid, line, context=context):
                    continue
                if line.product_id.ecotax_product_id and \
                    line.product_id.ecotax_product_id.id not in product_list.keys():
                    product_list.update({line.product_id.ecotax_product_id.id: line.product_qty})
                elif line.product_id.ecotax_product_id:
                    product_list[line.product_id.ecotax_product_id.id] += line.product_qty
                elif line.product_id.categ_id.ecotax_product_id and \
                    line.product_id.categ_id.ecotax_product_id.id not in product_list.keys():
                    product_list.update({line.product_id.categ_id.ecotax_product_id.id: line.product_qty})
                elif line.product_id.categ_id.ecotax_product_id:
                    product_list[line.product_id.categ_id.ecotax_product_id.id] += line.product_qty
            line_obj._genrate_ecotax_lines(cr, uid, purchase, product_list, context=context)
        return True
    
    def _amount_ecotax(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_ecotax': 0.0,
            }
            val = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                if line.ecotax:
                    
                    val += line.price_subtotal
            res[order.id]['amount_ecotax'] = cur_obj.round(cr, uid, cur, val)
        return res
    
    def _get_orders(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    _columns = {
        'amount_ecotax': fields.function(_amount_ecotax, digits_compute=dp.get_precision('Account'), 
            string='Included ecotax', store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'purchase.order.line': (_get_orders, ['price_unit', 'tax_id', 'discount', 'product_uom_qty', 'ecotax'], 20),
            },
            multi='sums', help="The included ecotax amount."),
    }
    
class purchase_order_line(orm.Model):
    _inherit = "purchase.order.line"
    
    _columns = {
        'ecotax': fields.boolean('Ecotax line'),
    }
    
    _defaults = {
        'ecotax': False,
    }
    
    def _genrate_ecotax_lines(self, cr, uid, purchase, product_list, context=None):
        if context is None:
            context = {}
        line_to_del_ids = self.search(cr, uid, [
                ('order_id', '=', purchase.id),
                ('ecotax', '=', True),
                ('state', '=', 'draft'),
            ], context=context)
        self.unlink(cr, uid, line_to_del_ids, context=context)
        for product_id in product_list.keys():
            res = self.onchange_product_id(cr, uid, [], purchase.pricelist_id.id, product_id, qty=product_list[product_id],
                    uom_id=False, partner_id=purchase.partner_id.id, date_order=purchase.date_order,
                    fiscal_position_id=purchase.fiscal_position and purchase.fiscal_position.id or False, context=context)
            vals = res.get('value')
            if vals:
                taxes_id = vals.get('taxes_id', [])
                vals.update({
                    'ecotax': True,
                    'order_id': purchase.id,
                    'product_id': product_id,
                    'product_qty': product_list[product_id],
                    'taxes_id': [(6, 0, taxes_id)],
                })
                self.create(cr, uid, vals, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
