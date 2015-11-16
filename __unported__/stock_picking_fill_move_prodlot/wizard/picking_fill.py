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

class stock_picking_fill(orm.TransientModel):
    
    _inherit = 'stock.picking.fill'
    
    _columns = {
        'prodlot_ids': fields.many2many('stock.production.lot', 'prodlot_fill_picking_rel', 'wizard_id', 'prodlot_id', 'Production lots'),
    }
    
    def _get_vals_prodlot(self, cr, uid, current, picking_id, location_id,
            location_dest_id, context=None):
        res = []
        move_obj = self.pool.get('stock.move')
        if not current.prodlot_ids:
            raise osv.except_osv(_('Invalid action !'),
                _('There are no production lot to add, please select at least 1 production lot to add to the picking !'))
        for prodlot in current.prodlot_ids:
            result_vals = move_obj.onchange_product_id(cr, uid, [], prod_id=prodlot.product_id.id,
                            loc_id=location_id, loc_dest_id=location_dest_id)
            line_vals = result_vals and result_vals.get('value') or False
            if line_vals:
                line_vals.update({
                    'picking_id': picking_id,
                    'product_id': prodlot.product_id.id,
                    'prodlot_id': prodlot.id
                })
                res.append(line_vals)
        return res
    
    def _get_vals(self, cr, uid, current, context=None):
        res = super(stock_picking_fill, self)._get_vals(cr, uid, current, context=context)
        picking = current.picking_id or False
        if not picking:
            return res
        else:
            picking_id = picking.id
            location_id = picking.location_id and picking.location_id.id or False
            location_dest_id = picking.location_dest_id and picking.location_dest_id.id or False
            if not location_id or not location_dest_id:
                return []
        if current.type_id.code == 'prodlot':
            res = self._get_vals_prodlot(cr, uid, current, picking_id=picking_id, location_id=location_id,
                    location_dest_id=location_dest_id, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
