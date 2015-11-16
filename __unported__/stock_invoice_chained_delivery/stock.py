# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
    _inherit = "stock.move"

    def _prepare_chained_picking(self, cr, uid, picking_name,
            picking, picking_type, moves_todo, context=None):
        res = super(stock_move, self)._prepare_chained_picking(
            cr, uid, picking_name, picking, picking_type, moves_todo, context=context)
        res['invoice_state'] = picking.invoice_state
        return res

    def create_chained_picking(self, cr, uid, moves, context=None):
        new_moves = super(stock_move, self).create_chained_picking(
            cr, uid, moves, context=context)
        picking_obj = self.pool.get('stock.picking')
        for picking, todo in self._chain_compute(cr, uid, moves, context=context).items():
            if picking and picking.type == 'out':
                picking_obj.write(cr, uid,
                                  picking.id, {'invoice_state': 'none'}, context=context)
        return new_moves

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
