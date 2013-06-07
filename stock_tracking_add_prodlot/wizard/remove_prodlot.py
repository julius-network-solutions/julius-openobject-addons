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

from osv import fields, osv
from tools.translate import _
import time
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class stock_packaging_remove_line(osv.osv_memory):

    _inherit = "stock.packaging.remove.line"
    _columns = {
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot'),
    }
            
stock_packaging_remove_line()

class stock_packaging_delete(osv.osv_memory):
    _inherit = "stock.packaging.delete"
    
    _columns = {
        'prodlot_ids': fields.one2many('stock.packaging.remove.line', 'parent_id', 'Lines'),
    }
    
    def _line_data(self, cr, uid, move):
        data = super(stock_packaging_delete, self)._line_data(cr, uid, move)
        data.update({
            'prodlot_id': move.prodlot_id and move.prodlot_id.id or False,
        })
        return data
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_packaging_delete, self).default_get(cr, uid, fields, context=context)
        prodlot_ids = []
        pack_id = context.get('active_id')
        move_ids = context.get('active_ids', [])
        pack_obj = self.pool.get('stock.tracking')
        move_obj = self.pool.get('stock.move')
        if not pack_id:
            return res
        if 'prodlot_ids' in fields:
            pack = pack_obj.browse(cr, uid, pack_id)
            move_ids = pack.current_move_ids
            prodlot = [self._line_data(cr, uid, m) for m in move_ids if m.prodlot_id]
            res.update(prodlot_ids=prodlot)
        return res
    
    def onchange_type_id(self, cr, uid, ids, type_id, pack_id):
        result = super(stock_packaging_delete, self).onchange_type_id(cr, uid, ids, type_id, pack_id)
        prodlot_ids = []
        domain_prodlot_id = []
        return result
    
    def _remove_prodlot(self, cr, uid, current, context=None):
        
        # Initialization #
        move_obj = self.pool.get('stock.move')
        tracking_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history')
        prodlot_obj = self.pool.get('stock.production.lot')
        date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if context == None:
            context = {}
        
        # History Tracking #
        hist_id = history_obj.create(cr, uid, {
           'tracking_id': current.pack_id.id,
           'type': 'move',
           'location_id': current.pack_id.location_id.id,
           'location_dest_id': current.pack_id.location_id.id,
        }, context=context)

        # Process #
        for line in current.product_ids:
            if line.delete:
                move_data = move_obj.browse(cr, uid, line.move_id.id, context=context)
                move_qty = move_data.product_qty
                # We can delete more product than allready present #
                if move_qty - line.quantity < 0:
                    raise osv.except_osv(_('Warning!'),_('Not enough product %s in this pack !') % (line.product_id.name))
                # If some product remain we create a resultant move #
                if move_qty - line.quantity != 0:
                    defaults = {
                        'location_id': current.pack_id.location_id.id,
                        'location_dest_id': current.pack_id.location_id.id,
                        'date': date,
                        'date_expected': date,
                        'tracking_id': current.pack_id.id,
                        'product_id': line.product_id.id,
                        'product_qty': move_qty - line.quantity,
                        'state': 'done',
                    }
                    move_obj.copy(cr, uid, line.move_id.id, default=defaults, context=context)
                # Creation of the erase move #
                defaults = {
                    'location_id': current.pack_id.location_id.id,
                    'location_dest_id': current.dest_location_id.id,
                    'date': date,
                    'date_expected': date,
                    'tracking_id': False,
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity,
                    'state': 'done',
                }
                move_obj.copy(cr, uid, line.move_id.id, default=defaults, context=context)
                move_obj.write(cr, uid, [line.move_id.id], {'pack_history_id': hist_id}, context=context)
                
                # Removal of the link between prodlot and pack TODO remove this custom field #
                prodlot_obj.write(cr, uid, line.prodlot_id.id, {'tracking_id': False}, context=context)
        
        tracking_obj.get_serials(cr, uid, [current.pack_id.id], context=context)
        tracking_obj.get_products(cr, uid, [current.pack_id.id], context=context)
        return True
    
    def delete_object(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        res = super(stock_packaging_delete, self).delete_object(cr, uid, ids, context=context)
        for current in self.browse(cr, uid, ids, context=context):
            type = current.type_id.code
            if type == 'prodlot':
                self._remove_prodlot(cr, uid, current, context=context)
        return res
       
stock_packaging_delete()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: