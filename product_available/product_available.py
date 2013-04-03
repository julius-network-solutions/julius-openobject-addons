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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_picking(osv.osv):
    _inherit = "stock.picking.out"

    def action_assign(self, cr, uid, ids, context):
        if context is None:
            context={}
        res={}
        for picking_id in self.browse(cr, uid, ids, context=context):
            move_lines = self.browse(cr, uid, picking_id.id, context=context).move_lines
            min_date=picking_id.min_date
            for move in move_lines:
                context['date_expected']=min_date
            res= super(stock_picking,self).action_assign(cr, uid, ids, context)
        return res
        
    def picking_order(self, cr, uid, ids, context):
        product_obj = self.pool.get('product.product')   
        for picking_id in ids:
            picking_data = self.browse(cr, uid, picking_id, context=context)
            move_lines = picking_data.move_lines
            for move in move_lines:
                product_id = move.product_id
                if product_id:
                    qty = move.product_qty
                    data = product_obj._product_available(cr, uid, [product_id.id], context=context)
                    test = data[product_id] 
                    if test< qty:
                        res = self.split(cr, uid, ids, data[product_id]['qty_available'], context=context)
        return res
        
stock_picking()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: