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

class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _calc_amount_untaxed_discounted(self, cr, uid, ids,
                                        name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            amount_untaxed = sale.amount_untaxed
            discount = (100 - sale.global_discount_percentage) / 100
            amount_untaxed_discounted = amount_untaxed * discount
            res[sale.id] = amount_untaxed_discounted
        return res

    def _calc_amount_tax_discounted(self, cr, uid, ids,
                                    name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            amount_tax = sale.amount_tax
            discount = (100 - sale.global_discount_percentage) / 100
            amount_tax_discounted = amount_tax * discount
            res[sale.id] = amount_tax_discounted
        return res

    def _calc_amount_total_discounted(self, cr, uid, ids,
                                      name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            res[sale.id] = sale.amount_untaxed_discounted + \
                sale.amount_tax_discounted
        return res

    def _check_if_discount(self, cr, uid, ids,
                           name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            res[sale.id] = False
            if sale.global_discount_percentage:
                res[sale.id] = True
            else:
                for line in sale.order_line:
                    if line.global_discount == True:
                        res[sale.id] = True
                        break
        return res

    _columns = {
        'global_discount_percentage': fields.float('Discount Percentage'),
        'amount_untaxed_discounted': fields.function(
            _calc_amount_untaxed_discounted,
            string='Untaxed Amount With Discount', readonly=True),
        'amount_tax_discounted': fields.function(
            _calc_amount_tax_discounted,
            string='Taxes With Discount', readonly=True),
        'amount_total_discounted': fields.function(
            _calc_amount_total_discounted,
            string='Total With Discount', readonly=True),
        'discount_is_present': fields.function(_check_if_discount,
            string='Discount Present',
            readonly=True, type="boolean"),
    }

    def generate_global_discount(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('sale.order.line')
        for sale in self.browse(cr, uid, ids, context=context):
            if sale.global_discount_percentage != 0.00:
                discount = sale.global_discount_percentage / 100
                res = 0
                for line in sale.order_line:
                    if line.global_discount == True:
                        line_obj.unlink(cr, uid, [line.id], context=context)
                    else:
                        qty = line.product_uom_qty
                        pu = line.price_unit
                        sub = qty * pu
                        res += sub
                discount_value = res * discount
                data_obj = self.pool.get('ir.model.data')
                model, product_id = data_obj.\
                    get_object_reference(cr, uid,
                                         'global_discount',
                                         'product_global_discount')
                res = line_obj.product_id_change(cr, uid, [],
                    pricelist=sale.pricelist_id.id,
                    product=product_id, qty=1,
                    partner_id=sale.partner_id.id,
                    lang=sale.partner_id.lang, update_tax=True,
                    date_order=sale.date_order,
                    fiscal_position=sale.fiscal_position,
                    context=context)
                value = res.get('value')
                if value:
                    tax_ids = value.get('tax_id') and \
                        [(6, 0, value.get('tax_id'))] or [(6, 0, [])]
                    value.update({
                        'global_discount': True,
                        'price_unit': -discount_value,
                        'order_id': sale.id,
                        'product_id': product_id,
                        'product_uom_qty': 1,
                        'product_uos_qty': 1,
                        'tax_id': tax_ids, 
                    })
                    line_obj.create(cr, uid, value, context=context)
                    self.write(cr, uid, sale.id, {
                        'global_discount_percentage': 0.00,
                        }, context=context)
        return True

class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    
    _columns = {
        'global_discount': fields.boolean('Global Discount'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
