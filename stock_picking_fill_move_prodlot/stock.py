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

    def update_stock_tracking_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return True
    
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
                    print 'product ids', product_ids
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
                    print 'flag', product_flag
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
