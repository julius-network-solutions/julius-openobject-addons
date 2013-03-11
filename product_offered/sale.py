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

    def _generate_offered(self, cr, uid, soids, context={}):
        # only one sale order at once.
        # should only be called from a wizard in a form view
        if len(soids) > 1:
            return False
        b_so = self.browse(cr, uid, soids[0], context)

#        euro_zone = (b_so.partner_invoice_id.country_id and \
#                        b_so.partner_invoice_id.country_id.in_euro_zone \
#                        or False)

        del_ids = []

        if b_so.state != 'draft':
            return False

        o_sol = self.pool.get('sale.order.line')

        for line in b_so.order_line:
            if line.offered:
                del_ids.append(line.id)

        o_sol.unlink(cr, uid, del_ids)

        b_so = self.browse(cr, uid, soids[0], context)
        for line in b_so.order_line:
            if line.product_id and line.product_id.offered_product:
                if line.product_uom_qty < line.product_id.offered_threshold:
                    continue
                offered_product = line.product_id.offered_product.id
                res = o_sol.product_id_change(cr, uid, list(),
                        b_so.pricelist_id.id,
                        offered_product, 1,
                        line.product_id.offered_product.uom_id.id, 1,
                        line.product_id.offered_product.uom_id.id,
                        line.name, b_so.partner_id.id)

                data = res['value']
                data.pop('weight')
                data.pop('tax_id')

                data['product_id'] = offered_product
                data['product_uos'] = data.pop('product_uos')[0]
                data['product_uom'] = data['product_uos']
                data['product_uom_qty'] = data['product_uos_qty']
                data['offered'] = True
                data['sequence'] = line.sequence + 1
                data['order_id'] = b_so.id
                data['date_planned'] = line.date_planned

#                if euro_zone:
#                    data['discount'] = 0.0
#                    data['price_unit'] = 0.0
#                else:
#                    data['discount'] = 100.0
#                    data['price_unit'] = 0.10

                if line.tax_id:
                    data['tax_id'] = [(6,0, [tax.id for tax in line.tax_id])]

                o_sol.create(cr, uid, data)

        # force computation of weight
        self.write(cr, uid, soids, {})
        return True


class costes_products_sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'offered' : fields.boolean('Offered'),
    }

    _defaults = {
        'offered' : lambda *args: False,
    }

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                                uom=False, qty_uos=0, uos=False, name='',
                                partner_id=False, lang=False):

        res = super(costes_products_sale_order_line, self).product_id_change(
                        cr, uid, ids, pricelist, product, qty,
                        uom, qty_uos, uos, name, partner_id, lang)

        # if product is changed let's force offered and discount
        # it will avoid some problems with computed offered lines
        res['value']['offered'] = False

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
