# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions (<http://www.julius.fr/>) contact@julius.fr
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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class stock_picking_fill(orm.TransientModel):
    
    _inherit = 'stock.picking.fill'
    
    def _get_vals_pack(self, cr, uid, current, picking_id, location_id,
            location_dest_id, context=None):
        res = []
        move_obj = self.pool.get('stock.move')
        if not current.pack_ids:
            raise osv.except_osv(_('Invalid action !'),
                _('There are no pack to add, please select at least 1 pack to add to the picking !'))
        for pack in current.pack_ids:
            product_lines = pack.child_product_ids
            serial_lines = pack.child_serial_ids
            prod_serial = {}
            prod_prod = {}
            tracking_id = pack.id
            for serial in serial_lines:
                prodlot = serial.serial_id
                result_vals = move_obj.onchange_product_id(cr, uid, [], prod_id=prodlot.product_id.id,
                                loc_id=location_id, loc_dest_id=location_dest_id)
                line_vals = result_vals and result_vals.get('value') or False
                if line_vals:
                    line_vals.update({'picking_id': picking_id})
                    line_vals.update({'product_id': prodlot.product_id.id})
                    line_vals.update({'prodlot_id': prodlot.id})
                    line_vals.update({'tracking_id': tracking_id})
                    res.append(line_vals)
                if not prodlot.product_id.id in prod_serial.keys():
                    prod_serial[prodlot.product_id.id] = 0
                prod_serial[prodlot.product_id.id] += serial.quantity or 0
            for product_line in product_lines:
                product = product_line.product_id
                line_quantity = product_line.quantity
                if product.id in prod_serial.keys():
                    line_quantity -= prod_serial.pop(product.id)
                if not product.id in prod_prod.keys():
                    prod_prod[product.id] = 0
                prod_prod[product.id] += line_quantity
            for product_id in prod_prod.keys():
                quantity = prod_prod[product_id]
                if quantity and quantity > 0:
                    result_vals = move_obj.onchange_product_id(cr, uid, [], prod_id=product_id,
                                    loc_id=location_id, loc_dest_id=location_dest_id)
                    line_vals = result_vals and result_vals.get('value') or False
                    if line_vals:
                        line_vals.update({
                            'picking_id': picking_id,
                            'product_id': product_id,
                            'product_qty': quantity,
                            'product_uos_qty': False,
                            'product_uos': False,
                            'tracking_id': tracking_id
                        })
                        res.append(line_vals)
        return res
    
    def _get_vals(self, cr, uid, current, context=None):
        res = super(stock_picking_fill, self)._get_vals(cr, uid, current, context=context)
        picking = current.picking_id or False
        if not picking:
            return res
        else:
            picking_id = picking.id
            location_id = picking.location_id and picking.location_id.id or False
            location_dest_id = picking.location_dest_id and picking.location_dest_id.id or False
            if not location_id or not location_dest_id:
                return []
        if current.type_id.code == 'pack':
            res = self._get_vals_pack(cr, uid, current, picking_id=picking_id, location_id=location_id,
                    location_dest_id=location_dest_id, context=context)
        return res
    
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location'),
        'pack_ids': fields.many2many('stock.tracking', 'pack_fill_picking_rel', 'wizard_id', 'pack_id', 'Packs',
                        domain=[('parent_id', '=', False),('state', '=', 'close')]),
    }
    
    def _get_location_id(self, cr, uid, context=None):
        if context == None:
            context = {}
        active_id = False
        location_id = False
        if context.get('active_id'):
            active_id = context.get('active_id')
        if active_id:
            picking_obj = self.pool.get('stock.picking')
            picking = picking_obj.browse(cr, uid, active_id, context=context)
            location_id = picking.location_id and picking.location_id.id or False
        return location_id
    
    _defaults = {
        'location_id': lambda self, cr, uid, context: self._get_location_id(cr, uid, context),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
