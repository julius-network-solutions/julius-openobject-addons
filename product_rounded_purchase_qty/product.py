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

class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'
    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        ## Init ##
        product_uom = self.pool.get('product.uom')
        product_product = self.pool.get('product.product')
        ## Original Function ##
        result = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id=pricelist_id, product_id=product_id, qty=qty, uom_id=uom_id,
            partner_id=partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, context=context)
        if not product_id:
            return result
        ## New Qty Computation ##
        if qty: 
            product = product_product.browse(cr, uid, product_id, context=context)
            new_product_qty = False
            for supplierinfo in product.seller_ids:
                new_product_qty = 0
                remaining_qty = qty
                if partner_id and (supplierinfo.name.id == partner_id):
                    min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                    while remaining_qty >= min_qty:
                        new_product_qty += min_qty
                        remaining_qty -= min_qty
                    if remaining_qty > 0:
                        new_product_qty += min_qty
            new_product_qty = new_product_qty or 1.0
            result['value'].update({'product_qty': new_product_qty})
        return result
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
