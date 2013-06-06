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
from tools.translate import _
from datetime import datetime

class stock_tracking(osv.osv):

    _inherit = 'stock.tracking'
    
    _columns = { 
        'state_pack': fields.selection([('purged','Purged')], 'Pack State', readonly=1),
    }
    
    def _create_move_copy(self, cr, uid, move_id, pack_data, date, parent_id, context=None):
        move_obj = self.pool.get('stock.move')
        defaults = {
                'location_id': pack_data.location_id.id,
                'location_dest_id': pack_data.location_id.id,
                'date': date,
                'date_expected': date,
                'tracking_id': parent_id,
                'state':'done',
            }
        new_id = move_obj.copy(cr, uid, move_id, default=defaults, context=context)
        return True
    
    def purge_pack(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        history_obj = self.pool.get('stock.tracking.history')
        date = datetime.now()
        if context == None:
            context = {}
        
        for pack_data in self.browse(cr, uid, ids, context=context):
            parent_id = False
            child_packs = pack_data.child_ids
            move_ids = pack_data.current_move_ids
            
            hist_id = history_obj.create(cr, uid, {
               'tracking_id': pack_data.id,
               'type': 'move',
               'location_id': pack_data.location_id.id,
               'location_dest_id': pack_data.location_id.id,
            }, context=context)
            
            if pack_data.parent_id:
                parent_id = pack_data.parent_id.id
                
            for child_data in child_packs:
                self.write(cr, uid, child_data.id, {'parent_id': parent_id}, context=context)
            
            for move in move_ids:
                self._create_move_copy(cr, uid, move.id, pack_data, date, parent_id, context=context)
                move_obj.write(cr, uid, [move.id], {'pack_history_id': hist_id}, context=context)
            self.write(cr, uid, pack_data.id, {'state_pack':'purged'}, context=context)
            self.get_products(cr, uid, [pack_data.id], context=context)
            self.get_serials(cr, uid, [pack_data.id], context=context)
        return True

stock_tracking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
