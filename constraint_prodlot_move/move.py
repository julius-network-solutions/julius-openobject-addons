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

from openerp.osv import fields, orm, osv
from openerp.tools.translate import _

class stock_move(orm.Model):  
    _inherit = 'stock.move'

    def _check_destination_id(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for move_data in self.browse(cr, uid, ids, context=context):
            if move_data.prodlot_id.id:
                if self.search(cr, uid, [('prodlot_id','=',move_data.prodlot_id.id),('state','=','done'),('date','>=',move_data.date)], context=context, limit=1):
                    return True
                location_id = move_data.location_id.id
                prodlot_id = move_data.prodlot_id.id
                current_location_id = move_data.prodlot_id.current_location_id.id
                if current_location_id and current_location_id != location_id:
                    name = move_data.prodlot_id.name
#                     raise osv.except_osv(_('Error'), _('The Origin of this move does not match the current position for this serial : %s') % name)
                    return False
        return True
        
    _constraints = [(_check_destination_id, 'The Origin of this move does not match the current position of this serial',['prodlot_id'])]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: