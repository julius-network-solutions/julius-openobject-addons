# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################

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
        'global_discount_percentage': fields.float('Discount Percentage',
            readonly=True,
            states={
                'draft':[('readonly',False)],
                'sent':[('readonly',False)],
                }),
        'amount_untaxed_discounted': fields.function(
            _calc_amount_untaxed_discounted,
            string='Untaxed Amount With Discount'),
        'amount_tax_discounted': fields.function(
            _calc_amount_tax_discounted,
            string='Taxes With Discount'),
        'amount_total_discounted': fields.function(
            _calc_amount_total_discounted,
            string='Total With Discount'),
        'discount_is_present': fields.function(_check_if_discount,
            string='Discount Present', type="boolean"),
    }

    def _get_lines_by_taxes(self, cr, uid, order_id, context=None):
        """ This method will return a dictionary of taxes as keys
        with the related lines.
        """
        if context is None:
            context = {}
        res = {}
        order = self.browse(cr, uid, order_id, context=context)
        for line in order.order_line:
            taxes = [x.id for x in line.tax_id]
            if taxes:
                taxes.sort()
            taxes_str = str(taxes)
            res.setdefault(taxes_str, [])
            res[taxes_str].append(line)
        return res

    def _create_global_discount_lines_by_taxes(self, cr, uid, discount,
                                               line_by_taxes, product_id,
                                               context=None):
        if context is None:
            context = {}
        res = []
        line_obj = self.pool.get('sale.order.line')
        for tax_str in line_by_taxes.keys():
            line_sum = 0
            discount_value = 0
            order = False
            line = False
            for line in line_by_taxes[tax_str]:
                qty = line.product_uom_qty
                pu = line.price_unit
                sub = qty * pu
                line_sum += sub
                discount_value = line_sum * discount
            if line:
                order = line.order_id
                res_value = line_obj.product_id_change(cr, uid, [],
                    pricelist=order.pricelist_id.id,
                    product=product_id, qty=1,
                    partner_id=order.partner_id.id,
                    lang=order.partner_id.lang, update_tax=False,
                    date_order=order.date_order,
                    fiscal_position=order.fiscal_position,
                    context=context)
                value = res_value.get('value')
                if value:
                    tax_ids = eval(tax_str)
                    tax_ids = [(6, 0, tax_ids)]
                    value.update({
                        'global_discount': True,
                        'price_unit': -discount_value,
                        'order_id': order.id,
                        'product_id': product_id,
                        'product_uom_qty': 1,
                        'product_uos_qty': 1,
                        'tax_id': tax_ids, 
                    })
                    res.append(line_obj.\
                        create(cr, uid, value, context=context))
        return res

    def generate_global_discount(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('sale.order.line')
        data_obj = self.pool.get('ir.model.data')
        for sale in self.browse(cr, uid, ids, context=context):
            if sale.state in ('draft','sent') and \
                sale.global_discount_percentage != 0.00:
                model, product_id = data_obj.\
                    get_object_reference(cr, uid,
                                         'global_discount',
                                         'product_global_discount')
                discount = sale.global_discount_percentage / 100
                global_line_ids = line_obj.\
                    search(cr, uid, [
                        ('order_id', '=', sale.id),
                        ('global_discount', '=', True),
                        ('state', '=', 'draft'),
                        ], context=context)
                line_obj.unlink(cr, uid, global_line_ids, context=context)
                global_line_ids = []
                line_by_taxes = self.\
                    _get_lines_by_taxes(cr, uid, sale.id, context=context)
                discount_line_ids = self.\
                    _create_global_discount_lines_by_taxes(cr, uid, discount,
                                                           line_by_taxes,
                                                           product_id,
                                                           context=context)
                self.write(cr, uid, sale.id, {
                    'global_discount_percentage': 0.00,
                    }, context=context)
        return True

    def _make_invoice(self, cr, uid, order, lines, context=None):
        if context is None:
            context = {}
        inv_id = super(sale_order, self).\
            _make_invoice(cr, uid, order, lines, context=None)
        if order.global_discount_percentage:
            invoice_obj = self.pool.get('account.invoice')
            data_obj = self.pool.get('ir.model.data')
            model, product_id = data_obj.\
                get_object_reference(cr, uid,
                                     'global_discount',
                                     'product_global_discount')
            discount = order.global_discount_percentage / 100
            line_by_taxes = invoice_obj.\
                    _get_lines_by_taxes(cr, uid, inv_id,
                                        context=context)
            invoice_ids = invoice_obj.\
                _create_global_discount_lines_by_taxes(cr, uid,
                                                       discount,
                                                       line_by_taxes,
                                                       product_id,
                                                       context=context)
            invoice_obj.button_compute(cr, uid, [inv_id])
        return inv_id

class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    
    _columns = {
        'global_discount': fields.boolean('Global Discount', readonly=True),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
