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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class stock_move(orm.Model):  
    _inherit = 'stock.move'

    def _check_pack_id(self, cr, uid, ids, context=None):
        for move_data in self.browse(cr, uid, ids, context=context):
            if move_data.prodlot_id:
                pack_id = move_data.tracking_id.id
                prodlot_id = move_data.prodlot_id.id
                date = move_data.date
                move_ids = self.search(cr, uid, [
                            ('id', '<>', move_data.id),
                            ('prodlot_id', '=', prodlot_id),
                            ('date', '<=', date),
                        ], limit=1, order='date desc', context=context)
                if move_data.tracking_id and move_ids:
                    move_id = move_ids[0]
                    previous_pack_id = self.browse(cr, uid, move_id, context=context).tracking_id.id
                    if (previous_pack_id and previous_pack_id != pack_id):
                        return False
        return True
        
    _constraints = [(_check_pack_id, 'This production lot is already in another Pack', ['prodlot_id'])]
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: