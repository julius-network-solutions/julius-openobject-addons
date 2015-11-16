# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions (<http://www.julius.fr/>) contact@julius.fr
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

class stock_production_lot(orm.Model):
    _inherit = 'stock.production.lot'

    def _get_current_tracking(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        serial_obj = self.pool.get('serial.stock.tracking')
        product_obj = self.pool.get('product.stock.tracking')
        move_obj = self.pool.get('stock.move')
        for prodlot in self.browse(cr, uid, ids, context=context):
            product_flag = False
            result[prodlot.id] = False
            move_ids = move_obj.search(cr, uid, [
                        ('prodlot_id','=',prodlot.id),
                        ('state','=','done')
                    ], order='date desc',context=context)
            if move_ids:
                move = move_obj.browse(cr, uid, move_ids[0], context=context)
                result[prodlot.id] = move.tracking_id.id
                if result[prodlot.id] is not False and move_obj.browse(cr, uid, move_ids[0], context=context).state == 'done':
                    serial_ids = serial_obj.search(cr, uid, [('serial_id','=',prodlot.id)], context=context)
                    product_ids = product_obj.search(cr, uid, [('product_id','=', prodlot.product_id.id),('tracking_id','=',prodlot.current_tracking_id.id)],context=context)
                    if move.tracking_id != prodlot.current_tracking_id:
                        product_flag = True
                    if serial_ids:
                        serial_obj.write(cr, uid, serial_ids, {'tracking_id' : result[prodlot.id], 'quantity': move.product_qty}, context=context)
                    else:
                        vals = {
                            'tracking_id': result[prodlot.id],
                            'serial_id': prodlot.id,
                            'product_id': move.product_id,
                            'quantity': move.product_qty,
                        }
                        serial_obj.create(cr, uid, vals, context=context)
                    if product_ids and product_flag:
                        for product in product_obj.browse(cr, uid, product_ids, context=context):
                            qty = product.quantity
                            product_qty = move.product_qty
                            delta = qty - product_qty
                            if delta == 0:
                                product_obj.unlink(cr, uid, product_ids, context=context)
                            else:
                                product_obj.write(cr, uid, product_ids, {'quantity': delta}, context=context)
        return result

    def _get_prod_lot(self, cr, uid, ids, context=None):
        res = set()
        obj = self.pool.get('stock.move')
        for move in obj.browse(cr, uid, ids, context=context):
            res.add(move.prodlot_id.id)
        return list(res)
    
    _columns = {
        'current_tracking_id': fields.function(_get_current_tracking, type='many2one',
                relation='stock.tracking', string='Current Tracking', store={
                'stock.production.lot':
                    (lambda self, cr, uid, ids, c=None: ids, ['move_ids'], 10),
                'stock.move':
                    (_get_prod_lot, [], 20),
                }),
    }

#     def write(self, cr, uid, ids, vals, context=None):
#         """
#         Inherit the write method for stock production lot.
#         If the prodlot got any modification on his related moves
#         run the method to update the tracking values
#         """
#         if context is None:
#             context = {}
#         res = super(stock_production_lot, self).\
#             write(cr, uid, ids, vals, context=context)
#         if vals.get('move_ids'):
#             # If there are some modifications done on the
#             # current prodlot moves, we update the tracking values
#             if not isinstance(ids, list):
#                 ids = [ids]
#             self.update_stock_tracking_data(cr, uid, ids, context=context)
#         return res
# 
#     def update_stock_tracking_data(self, cr, uid, ids, context=None):
#         """
#         This method if the method which update the tracking values
#         with updating serials and products inside a tracking object
#         """
#         if context is None:
#             context = {}
#         serial_obj = self.pool.get('serial.stock.tracking')
#         product_obj = self.pool.get('product.stock.tracking')
#         move_obj = self.pool.get('stock.move')
#         for prodlot in self.browse(cr, uid, ids, context=context):
#             # For all prodlots and one by one,
#             # we are looking for the last move done on it
#             # If the last move done is not inside the current tracking defined
#             # Update the values to move it to the other tracking
#             product_flag = False
#             tracking_id = False
#             move_ids = move_obj.search(cr, uid, [
#                     ('prodlot_id', '=', prodlot.id),
#                     ('state', '=', 'done'),
#                 ], limit=1, order='date desc', context=context)
#             if move_ids:
#                 move = move_obj.browse(cr, uid, move_ids[0], context=context)
#                 tracking_id = move.tracking_id and move.tracking_id.id or False
#                 if tracking_id:
#                     serial_ids = serial_obj.search(cr, uid, [
#                         ('serial_id', '=', prodlot.id),
#                         ], context=context)
#                     if tracking_id != prodlot.current_tracking_id.id:
#                         product_flag = True
#                     vals = {
#                         'tracking_id': tracking_id,
#                         'quantity': move.product_qty,
#                     }
#                     if serial_ids:
#                         serial_obj.write(cr, uid, serial_ids,
#                                          vals, context=context)
#                     else:
#                         vals.update({
#                             'serial_id': prodlot.id,
#                             'product_id': move.product_id,
#                         })
#                         serial_obj.create(cr, uid, vals, context=context)
#                     product_ids = product_obj.search(cr, uid, [
#                         ('product_id', '=', prodlot.product_id.id),
#                         ('tracking_id', '=', prodlot.current_tracking_id.id),
#                         ], context=context)
#                     if product_ids and product_flag:
#                         for product in product_obj.browse(cr, uid,
#                                                           product_ids,
#                                                           context=context):
#                             qty = product.quantity
#                             product_qty = move.product_qty
#                             delta = qty - product_qty
#                             if delta == 0:
#                                 product_obj.unlink(cr, uid,
#                                                    product_ids,
#                                                    context=context)
#                             else:
#                                 product_obj.write(cr, uid, product_ids,
#                                                   {'quantity': delta},
#                                                   context=context)
#         return True
# 
# class stock_move(orm.Model):
#     _inherit = 'stock.move'
# 
#     def create(self, cr, uid, vals, context=None):
#         """
#         Inherit the create method for stock move.
#         If the move got a prodlot_id run the method
#         to update the tracking the tracking values
#         """
#         if context is None:
#             context = {}
#         res = super(stock_move, self).\
#             create(cr, uid, vals, context=context)
#         if vals.get('prodlot_id'):
#             # If there is a prodlot define
#             # We update the tracking values
#             prodlot_obj = self.pool.get('stock.production.lot')
#             prodlot_obj.update_stock_tracking_data(cr, uid,
#                                                    [vals.get('prodlot_id')],
#                                                    context=context)
#         return res
# 
#     def write(self, cr, uid, ids, vals, context=None):
#         """
#         Inherit the write method for stock move.
#         If the move got a prodlot_id or remove a prodlot
#         run the method to update the tracking values
#         """
#         if context is None:
#             context = {}
#         # Get all prodlots which are defined before the write,
#         # and by the current modification.
#         prodlot_ids = vals.get('prodlot_id') and [vals['prodlot_id']] or []
#         if vals.has_key('prodlot_id'):
#             if isinstance(ids, (int, long)):
#                 ids = [ids]
#             for move in self.browse(cr, uid, ids, context=context):
#                 if move.prodlot_id and move.prodlot_id.id not in prodlot_ids:
#                     prodlot_ids.append(move.prodlot_id.id)
#         res = super(stock_move, self).\
#             write(cr, uid, ids, vals, context=context)
#         if prodlot_ids:
#             # If there are some modifications done on prodlot_id,
#             # We update here the tracking values.
#             prodlot_obj = self.pool.get('stock.production.lot')
#             prodlot_obj.update_stock_tracking_data(cr, uid,
#                                                    prodlot_ids,
#                                                    context=context)
#         return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
