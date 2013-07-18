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
    
    def _get_offered_line_vals(self, cr, uid, line, order, multiple, context=None):
        if context is None:
            context = {}
        o_sol = self.pool.get('sale.order.line')
        # If there is no product define, the system take the same product
        offered_product = line.product_id.offered_product_id or line.product_id
        res = o_sol.product_id_change(cr, uid, list(),
                order.pricelist_id.id, offered_product.id, qty=1,
                uom=offered_product.uom_id.id,
                qty_uos=1, uos=offered_product.uom_id.id,
                name='', partner_id=order.partner_id.id, lang=order.partner_id.lang,
                update_tax=True, date_order=order.date_order,
                packaging=False, fiscal_position=order.fiscal_position,
                flag=False, context=context)
        vals = res['value']
        uom_id = offered_product and offered_product.uom_id.id or False
        quantity = multiple and (int(line.product_uom_qty / line.product_id.offered_threshold) \
                            * line.product_id.offered_qty) or line.product_id.offered_qty
        vals.update({
            'product_id': offered_product.id,
            'product_uos': uom_id,
            'product_uos_qty': quantity,
            'product_uom': uom_id,
            'product_uom_qty': quantity,
            'offered': True,
            'sequence': line.sequence + 1,
            'order_id': order.id,
            'discount': 100.0,
            'th_weight': False,
        })
        vals['name'] += _(' offered')
        return vals

    def _generate_offered(self, cr, uid, ids, multiple, context=None):
        if context is None:
            context = {}
        o_sol = self.pool.get('sale.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            # If this order is not in draft state we continue
            if order.state not in ('sent','draft'):
                continue
            # Delete all the existing offer lines existing in the current sale order
            del_ids = []
            for line in order.order_line:
                if line.offered:
                    del_ids.append(line.id)
            o_sol.unlink(cr, uid, del_ids, context=context)
            
            # This will create the lines if there is a offered threshold
            # and a offered qty
            for line in order.order_line:
                if line.product_id and line.product_id.offered_threshold and line.product_id.offered_qty:
                    # If the quantity of the line is lower than the offered threshold
                    # don't do the function for this line
                    if line.product_uom_qty < line.product_id.offered_threshold:
                        continue
                    vals = self._get_offered_line_vals(cr, uid, line, order, multiple, context=context)
                    o_sol.create(cr, uid, vals, context=context)
            # force computation of weight
            self.write(cr, uid, order.id, {}, context=context)
        return True
    
    def generate_offered(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        multiple = context.get('multiple',True)
        return self._generate_offered(cr, uid, ids, multiple, context=context)

class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'offered' : fields.boolean('Offered'),
    }

    _defaults = {
        'offered' : lambda *args: False,
    }
    
    def on_change_offered(self, cr, uid, ids, offered, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        if context is None:
            context = {}
        res = {}
        product_obj = self.pool.get('product.product')
        if offered:
            price = 0.10
            res = {
                'value': {
                    'price_unit': price,
                    'discount': 100,
                }
            }
        else:
            prod_change_val = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
            price = prod_change_val.get('value') and prod_change_val['value'].get('price_unit') or 0.0
            discount = prod_change_val.get('value') and prod_change_val['value'].get('discount') or 0.0
            res = {
                'value': {
                    'price_unit': price,
                    'discount': discount,
                }
            }
        return res

#    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
#                                uom=False, qty_uos=0, uos=False, name='',
#                                partner_id=False, lang=False):
#
#        res = super(costes_products_sale_order_line, self).product_id_change(
#                        cr, uid, ids, pricelist, product, qty,
#                        uom, qty_uos, uos, name, partner_id, lang)
#
#        # if product is changed let's force offered and discount
#        # it will avoid some problems with computed offered lines
#        res['value']['offered'] = False
#
#        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
