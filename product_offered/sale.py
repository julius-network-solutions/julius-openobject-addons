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

class costes_products_sale_order(orm.Model):
    _inherit = 'sale.order'
    
    def _get_offered_line_vals(self, cr, uid, line, order, context=None):
        if context is None:
            context = {}
        o_sol = self.pool.get('sale.order.line')
        offered_product = line.product_id.offered_product_id.id
        res = o_sol.product_id_change(cr, uid, list(),
                order.pricelist_id.id, offered_product, qty=1,
                uom=line.product_id.offered_product_id.uom_id.id,
                qty_uos=1, uos=line.product_id.offered_product_id.uom_id.id,
                name='', partner_id=order.partner_id.id, lang=order.partner_id.lang,
                update_tax=True, date_order=order.date_order,
                packaging=False, fiscal_position=order.fiscal_position,
                flag=False, context=context)
        vals = res['value']
        uom_id = vals.get('product_uos') and uom[0] or line.product_id.offered_product_id.uom_id.id or False
        quantity = int(line.product_uom_qty / line.product_id.offered_threshold) * line.product_id.offered_qty
        vals.update({
            'product_id': offered_product,
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

    def _generate_offered(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        o_sol = self.pool.get('sale.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            # If this order is not in draft state we continue
            if order.state != 'draft':
                continue
            # Delete all the existing offer lines existing in the current sale order
            del_ids = []
            for line in order.order_line:
                if line.offered:
                    del_ids.append(line.id)
            o_sol.unlink(cr, uid, del_ids, context=context)

#        euro_zone = (b_so.partner_invoice_id.country_id and \
#                        b_so.partner_invoice_id.country_id.in_euro_zone \
#                        or False)

            for line in order.order_line:
                if line.product_id and line.product_id.offered_product_id:
                    # If the quantity of the line is lower than the offered threshold
                    # don't do the function for this line
                    if line.product_uom_qty < line.product_id.offered_threshold:
                        continue
                    vals = self._get_offered_line_vals(cr, uid, line, order, context=context)
                    
    #                if euro_zone:
    #                    data['discount'] = 0.0
    #                    data['price_unit'] = 0.0
    #                else:
    #                    data['discount'] = 100.0
    #                    data['price_unit'] = 0.10
    
                    o_sol.create(cr, uid, vals, context=context)
    
            # force computation of weight
            self.write(cr, uid, order.id, {}, context=context)
        return True


class costes_products_sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'offered' : fields.boolean('Offered'),
    }

    _defaults = {
        'offered' : lambda *args: False,
    }

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
