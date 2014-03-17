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

from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.sale.sale import sale_order

class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').\
            browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(sale_order._amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}:
                               ids, ['order_line'], 10),
                'sale.order.line': (_get_order,
                                    ['price_unit', 'tax_id',
                                     'discount', 'product_uom_qty',
                                     'launch_costs'], 10),
            },
            multi='sums', help="The amount without tax.",
            track_visibility='always'),
        'amount_tax': fields.function(sale_order._amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}:
                               ids, ['order_line'], 10),
                'sale.order.line': (_get_order,
                                    ['price_unit', 'tax_id',
                                     'discount', 'product_uom_qty',
                                     'launch_costs'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(sale_order._amount_all,
            digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}:
                               ids, ['order_line'], 10),
                'sale.order.line': (_get_order,
                                    ['price_unit', 'tax_id',
                                     'discount', 'product_uom_qty',
                                     'launch_costs'], 10),
            },
            multi='sums', help="The total amount."),
    }

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = super(sale_order, self).\
            _amount_line_tax(cr, uid, line, context=context)
        data_obj = self.pool.get('ir.model.data')
        product_obj = self.pool.get('product.product')
        model, product_id = data_obj.get_object_reference(
            cr, uid, 'launch_costs', 'product_launch_costs')
        product = product_obj.browse(cr, uid, product_id, context=context)
        for c in self.pool.get('account.tax').\
            compute_all(cr, uid, line.tax_id, line.launch_costs,
                        1, product, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        data_obj = self.pool.get('ir.model.data')
        model, product_id = data_obj.get_object_reference(
            cr, uid, 'launch_costs', 'product_launch_costs')
        if context is None:
            context = {}
        res = super(sale_order_line, self).\
            _amount_line(cr, uid, ids, field_name, arg, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            price = line.launch_costs or 0
            if price:
                taxes = tax_obj.\
                    compute_all(cr, uid, line.tax_id,
                                price, 1, product_id,
                                line.order_id.partner_id)
                cur = line.order_id.pricelist_id.currency_id
                res.setdefault(line.id, 0.0)
                res[line.id] += cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'price_subtotal': fields.function(_amount_line,
            string='Subtotal', digits_compute=dp.get_precision('Account')),
        'launch_costs' : fields.float('Launch Costs'),
        'launch_costs_line_id': fields.many2one('account.invoice.line', 'Launch Costs invoice line'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        default['launch_costs_line_id'] = False
        return super(sale_order_line, self).copy(cr, uid, id, default, context=context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        default['launch_costs_line_id'] = False
        return super(sale_order_line, self).copy_data(cr, uid, id, default, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: