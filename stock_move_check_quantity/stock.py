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
from openerp import tools
from openerp.tools.translate import _

class stock_move(orm.Model):
    _inherit = 'stock.move'
    
    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False,
                        loc_id=False, product_id=False, uom_id=False, context=None):
        """ On change of production lot gives a warning message.
        @param prodlot_id: Changed production lot id
        @param product_qty: Quantity of product
        @param loc_id: Location id
        @param product_id: Product id
        @return: Warning message
        """
        if not prodlot_id or not loc_id:
            return {}
        ctx = context and context.copy() or {}
        ctx['location_id'] = loc_id
        ctx.update({'raise-exception': True})
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        product_uom = product_obj.browse(cr, uid, product_id, context=ctx).uom_id
        prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, context=ctx)
        location = self.pool.get('stock.location').browse(cr, uid, loc_id, context=ctx)
        uom = uom_obj.browse(cr, uid, uom_id, context=ctx)
        amount_actual = uom_obj._compute_qty_obj(cr, uid, product_uom, prodlot.stock_available, uom, context=ctx)
        if (location.usage == 'internal') and (product_qty > (amount_actual or 0.0)):
            raise orm.except_orm(_('Error'), _('Insufficient Stock for Serial Number ! , You are moving  %s (%s) but only %s (%s) available for this serial number.') % (product_qty, uom.name, amount_actual, uom.name))
        return True
    
    def _check_quantity(self, cr, uid, ids, context=None):
        for move_data in self.browse(cr, uid, ids, context=context):
            if move_data.product_id.id and move_data.location_id.usage == 'internal' and move_data.location_id and move_data.state not in ('draft','confirmed','waiting','done','cancel'):
                if not move_data.prodlot_id.id:
                    qty = move_data.product_qty
                    qty_on_hand = move_data.product_id.qty_available
                    res = qty_on_hand - qty
                    if res < 0:
                        qty_on_hand_real = qty_on_hand
                        name = move_data.product_id.name
                        raise orm.except_orm(_('Error'), _('The Product %s has not enough quantity on hand (%s)') % (name,qty_on_hand_real))
                        return False
                else:
                    qty = move_data.product_qty
                    qty_on_hand = move_data.prodlot_id.stock_available
                    res = qty_on_hand - qty
                    if res < 0:
                        name = move_data.prodlot_id.name
                        raise orm.except_orm(_('Error'), _('The Prodlot %s has not enough quantity on hand (%s)') % (name,qty_on_hand))
                        return False
        return True
    
    
    _constraints = [
        (_check_quantity, 
         'The Origin of this move does not match the current position of this serial',
         ['prodlot_id'])
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: