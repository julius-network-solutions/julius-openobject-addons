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

    _name = "stock.packaging.remove.line"
    _description = "Remove object to a pack"
    
    _columns = {
        'parent_id': fields.many2one('stock.packaging.delete', 'Parent'),
        'product_id': fields.many2one('product.product', 'Product'),
        'move_id': fields.many2one('stock.move', 'Move'),
        'quantity': fields.float('Quantity'),
        'delete': fields.boolean('Delete'),
    }
    
    _defaults = {
        'quantity': 1.0,
        'delete': False,
    }
            
stock_packaging_remove_line()

class stock_packaging_delete(osv.osv_memory):
    _name = "stock.packaging.delete"
    
    _columns = {        
        'type_id': fields.many2one('stock.packaging.add.type', 'Type', required=True),
        'type': fields.char('Type', size=64),
        'pack_id': fields.many2one('stock.tracking', 'Pack'),
        'product_ids': fields.one2many('stock.packaging.remove.line', 'parent_id', 'Lines'),
        'dest_location_id': fields.many2one('stock.location', 'Destination Location'),
    }
    
    def _get_type_id(self, cr, uid, context):
        if context == None:
            context = {}
        if context.get('type_selection'):
            type = context.get('type_selection')
        else:
            type = 'product'
        type_obj = self.pool.get('stock.packaging.add.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        return default_type and default_type[0] or False
    
    def _get_type(self, cr, uid, context=None):
        if context == None:
            context = {}
        if context.get('type_selection'):
            type = context.get('type_selection')
        else:
            type = 'product'
        res_type = ''
        type_obj = self.pool.get('stock.packaging.add.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        if default_type and default_type[0]:
            read_type = type_obj.read(cr, uid, default_type[0], ['code'], context=context)
            if read_type['code']:
                res_type = read_type['code']
        return res_type or ''
    
    _defaults = {
        'pack_id': lambda self, cr, uid, context: context.get('active_id') or False,
        'type_id': lambda self, cr, uid, context: self._get_type_id(cr, uid, context),
        'type': lambda self, cr, uid, context: self._get_type(cr, uid, context),
    }
    
    def _line_data(self, cr, uid, move):
        data = {
            'product_id' : move.product_id and move.product_id.id or False,
            'quantity' : move.product_qty or 0,
            'move_id': move.id,
        }
        return data
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_packaging_delete, self).default_get(cr, uid, fields, context=context)
        product_ids = []
        pack_id = context.get('active_id')
        move_ids = context.get('active_ids', [])
        pack_obj = self.pool.get('stock.tracking')
        move_obj = self.pool.get('stock.move')
        if not pack_id:
            return res
        if 'product_ids' in fields:
            pack = pack_obj.browse(cr, uid, pack_id)
            move_ids = pack.current_move_ids
            product = [self._line_data(cr, uid, m) for m in move_ids if not m.prodlot_id]
            res.update(product_ids=product)
        return res
    
    def onchange_type_id(self, cr, uid, ids, type_id, pack_id):
        context = {}
        product_ids = []
        domain_product_id = []
        res = {'value': {'type': ''}}
        type_obj = self.pool.get('stock.packaging.add.type')
        if type_id:
            type = type_obj.read(cr, uid, type_id, ['code'])
            if type['code']:
                res = {'value': {'type': type['code']}}
        return res
        
    def _delete_products(self, cr, uid, current, context=None):
        
        # Initialization #
        move_obj = self.pool.get('stock.move')
        tracking_obj = self.pool.get('stock.tracking')
        history_obj = self.pool.get('stock.tracking.history')
        date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if context == None:
            context = {}
        
        # History Tracking #
        hist_id = history_obj.create(cr, uid, {
           'tracking_id': current.pack_id.id,
           'type': 'move',
           'location_id': current.pack_id.location_id.id,
           'location_dest_id': current.dest_location_id.id,
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
                
        tracking_obj.get_products(cr, uid, [current.pack_id.id], context=context)
        return True
    
    def delete_object(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        for current in self.browse(cr, uid, ids, context=context):
            type = current.type_id.code
            if type == 'product':
                self._delete_products(cr, uid, current, context=context)
        return {'type': 'ir.actions.act_window_close'}
    
stock_packaging_delete()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: