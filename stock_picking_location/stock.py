# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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

from osv import osv, fields

class stock_picking(osv.osv):
    
    _inherit = 'stock.picking'
    
    _columns = {
        'location_default_id': fields.many2one('stock.location', 'Default move location'),
        'location_dest_default_id': fields.many2one('stock.location', 'Default move dest. location'),
    }
    
stock_picking()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    def _get_default_location(self, cr, uid, field='location_id', context=None):
        picking_obj = self.pool.get('stock.picking')
        res = False
        if context == None:
            context = {}
        if context.get('picking_id'):
            picking_id = context.get('picking_id')
            if picking_id:
                picking = picking_obj.browse(cr, uid, picking_id, context=context)
                if field == 'location_dest_id':
                    res = picking.location_dest_default_id and picking.location_dest_default_id.id or False
                else:
                    res = picking.location_default_id and picking.location_default_id.id or False
        return res
    
    _defaults = {
        'location_id': lambda self, cr, uid, context: context.get('picking_id', False) and self._get_default_location(cr, uid, 'location_id', context) or False,
        'location_dest_id': lambda self, cr, uid, context: context.get('picking_id', False) and self._get_default_location(cr, uid, 'location_dest_id', context) or False,
    }
    
stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
