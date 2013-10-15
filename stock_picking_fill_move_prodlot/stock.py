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

class stock_production_lot(orm.Model):
    
    _inherit = 'stock.production.lot'
    
    def _get_current_location(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        move_obj = self.pool.get('stock.move')
        for prodlot in self.browse(cr, uid, ids, context=context):
            result[prodlot.id] = False
            move_ids = move_obj.search(cr, uid, [
                        ('prodlot_id','=',prodlot.id),
                        ('state','=','done')
                    ], order='date desc',context=context)
            if move_ids:
                result[prodlot.id] = move_obj.browse(cr, uid, move_ids[0], context=context).location_dest_id.id
        return result
    
    def _get_current_tracking(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        serial_obj = self.pool.get('serial.stock.tracking')
        move_obj = self.pool.get('stock.move')
        for prodlot in self.browse(cr, uid, ids, context=context):
            result[prodlot.id] = False
            move_ids = move_obj.search(cr, uid, [
                        ('prodlot_id','=',prodlot.id),
                        ('state','=','done')
                    ], order='date desc',context=context)
            if move_ids:
                result[prodlot.id] = move_obj.browse(cr, uid, move_ids[0], context=context).tracking_id.id
                if result[prodlot.id] is not False and move_obj.browse(cr, uid, move_ids[0], context=context).state == 'done':
                    serial_ids = serial_obj.search(cr, uid, [('serial_id','=',prodlot.id)], context=context)
                    if ids:
                        serial_obj.write(cr, uid, serial_ids, {'tracking_id' : result[prodlot.id]}, context=context)
                    else:
                        vals = {
                            'tracking_id': result[prodlot.id],
                            'serial_ids': prodlot.id,
                            'quantity': move_obj.browse(cr, uid, move_ids[0], context=context).quantity
                        }
                        serial_obj.create(cr, uid, vals, context=context)
        return result

    def _get_prod_lot(self, cr, uid, ids, context=None):
        res = set()
        obj = self.pool.get('stock.move')
        for move in obj.browse(cr, uid, ids, context=context):
            res.add(move.prodlot_id.id)
        return list(res)
    
    _columns = {
        'current_location_id': fields.function(_get_current_location, type='many2one',
                relation='stock.location', string='Current Location', store={
                'stock.production.lot':
                    (lambda self, cr, uid, ids, c=None: ids, ['move_ids'], 10),
                'stock.move':
                    (_get_prod_lot, [], 20),
                }),
        'current_tracking_id': fields.function(_get_current_tracking, type='many2one',
                relation='stock.tracking', string='Current Tracking', store={
                'stock.production.lot':
                    (lambda self, cr, uid, ids, c=None: ids, ['move_ids'], 10),
                'stock.move':
                    (_get_prod_lot, [], 20),
                }),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
