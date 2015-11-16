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

class stock_move(orm.Model):
    _inherit = 'stock.move'
    
    def _get_default_location(self, cr, uid, field='location_id', context=None):
        picking_obj = self.pool.get('stock.picking')
        res = False
        if context is None:
            context = {}
        if context.get('picking_id'):
            picking_id = context.get('picking_id')
            if picking_id:
                picking = picking_obj.browse(cr, uid, picking_id, context=context)
                if field == 'location_dest_id':
                    res = picking.location_dest_id and picking.location_dest_id.id or False
                else:
                    res = picking.location_id and picking.location_id.id or False
        return res
    
    def onchange_move_type(self, cr, uid, ids, type, context=None):
        """ On change of move type gives sorce and destination location.
        @param type: Move Type
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        location_id = False
        location_dest_id = False
        if context.get('location_id') or context.get('location_dest_id'):
            location_id = context.get('location_id')
            location_dest_id = context.get('location_dest_id')
            return {
                'value': {
                    'location_id': location_id or self._get_default_location(cr, uid, field='location_id', context=context),
                    'location_dest_id': location_dest_id or self._get_default_location(cr, uid, field='location_dest_id', context=context)}
                }
        elif context.get('picking_id'):
            return {
                'value': {
                    'location_id': self._get_default_location(cr, uid, field='location_id', context=context),
                    'location_dest_id': self._get_default_location(cr, uid, field='location_dest_id', context=context)}
                }
        else:
            return super(stock_move, self).onchange_move_type(cr, uid, ids, type, context=context)
        return {'value':{'location_id': source_location and source_location[1] or False, 'location_dest_id': dest_location and dest_location[1] or False}}
    
    _defaults = {
        'location_id': lambda self, cr, uid, context: context.get('picking_id', False)
                and self._get_default_location(cr, uid, 'location_id', context) or False,
        'location_dest_id': lambda self, cr, uid, context: context.get('picking_id', False)
                and self._get_default_location(cr, uid, 'location_dest_id', context) or False,
    }
    
#class stock_picking(orm.Model):
#    _inherit = 'stock.picking.in'
#    
#    def onchange_location(self, cr, uid, ids, location_id, context=None):
#        if context is None:
#            context = {}
#        stock_move_obj = self.pool.get('stock.move')
#        if ids:
#            pick = self.browse(cr, uid, ids[0], context=context)
#            for move in pick.move_lines:
#                if move.location_id is False or move.location_id != location_id:
#                    stock_move_obj.write(cr, uid, [move.id], {'location_id': location_id}, context=context)
#        return True
#    
#    def onchange_location_dest(self, cr, uid, ids, location_dest_id, context=None):
#        if context is None:
#            context = {}
#        stock_move_obj = self.pool.get('stock.move')
#        if ids:
#            pick = self.browse(cr, uid, ids[0], context=context)
#            for move in pick.move_lines:
#                if move.location_dest_id is False or move.location_dest_id != location_dest_id:
#                    stock_move_obj.write(cr, uid, [move.id], {'location_dest_id': location_dest_id}, context=context)
#        return True
class stock_picking_in(orm.Model):
    _inherit = 'stock.picking.in'
    
    def onchange_location(self, cr, uid, ids, location_id, context=None):
        if context is None:
            context = {}
        stock_move_obj = self.pool.get('stock.move')
        if ids:
            pick = self.browse(cr, uid, ids[0], context=context)
            for move in pick.move_lines:
                if move.location_id is False or move.location_id != location_id:
                    stock_move_obj.write(cr, uid, [move.id], {'location_id': location_id}, context=context)
        return True
    
    def onchange_location_dest(self, cr, uid, ids, location_dest_id, context=None):
        if context is None:
            context = {}
        stock_move_obj = self.pool.get('stock.move')
        if ids:
            pick = self.browse(cr, uid, ids[0], context=context)
            for move in pick.move_lines:
                if move.location_dest_id is False or move.location_dest_id != location_dest_id:
                    stock_move_obj.write(cr, uid, [move.id], {'location_dest_id': location_dest_id}, context=context)
        return True
    
class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    def onchange_location(self, cr, uid, ids, location_id, context=None):
        if context is None:
            context = {}
        stock_move_obj = self.pool.get('stock.move')
        if ids:
            pick = self.browse(cr, uid, ids[0], context=context)
            for move in pick.move_lines:
                if move.location_id is False or move.location_id != location_id:
                    stock_move_obj.write(cr, uid, [move.id], {'location_id': location_id}, context=context)
        return True
    
    def onchange_location_dest(self, cr, uid, ids, location_dest_id, context=None):
        if context is None:
            context = {}
        stock_move_obj = self.pool.get('stock.move')
        if ids:
            pick = self.browse(cr, uid, ids[0], context=context)
            for move in pick.move_lines:
                if move.location_dest_id is False or move.location_dest_id != location_dest_id:
                    stock_move_obj.write(cr, uid, [move.id], {'location_dest_id': location_dest_id}, context=context)
        return True
    
class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def onchange_location(self, cr, uid, ids, location_id, context=None):
        if context is None:
            context = {}
        stock_move_obj = self.pool.get('stock.move')
        if ids:
            pick = self.browse(cr, uid, ids[0], context=context)
            for move in pick.move_lines:
                if move.location_id is False or move.location_id != location_id:
                    stock_move_obj.write(cr, uid, [move.id], {'location_id': location_id}, context=context)
        return True
    
    def onchange_location_dest(self, cr, uid, ids, location_dest_id, context=None):
        if context is None:
            context = {}
        stock_move_obj = self.pool.get('stock.move')
        if ids:
            pick = self.browse(cr, uid, ids[0], context=context)
            for move in pick.move_lines:
                if move.location_dest_id is False or move.location_dest_id != location_dest_id:
                    stock_move_obj.write(cr, uid, [move.id], {'location_dest_id': location_dest_id}, context=context)
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
