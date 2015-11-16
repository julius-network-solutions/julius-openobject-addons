# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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
from openerp import tools
from openerp.tools.translate import _

class split_in_production_lot(orm.TransientModel):
    _inherit = "stock.move.split"
    _description = "Split in Production lots"
    
    _columns = {
        'use_exist' : fields.boolean('Existing Lots', invisible=True),
     }
    _defaults = {
        'use_exist': True,
    }
    def default_get(self, cr, uid, fields, context=None):
        res = super(split_in_production_lot, self).default_get(cr, uid, fields, context=context)
        res.update({'use_exist': True})
        return res
        
    def create_prodlot(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        prodlot_obj = self.pool.get('stock.production.lot')
        wizard_line_obj = self.pool.get('stock.move.split.lines')
        data_pool = self.pool.get('ir.model.data')
        qty = range(int(self.browse(cr, uid, ids[0], context=context).qty))
        action_model, action_id = data_pool.get_object_reference(
            cr, uid, 'stock', "track_line")
        action_pool = self.pool.get(action_model)
        action = action_pool.read(cr, uid, action_id, context=context)
        for x in qty:
            for this in self.browse(cr, uid, ids, context=context):
                if this.product_id and this.qty > 0 and this.product_id.track_production:
                    prodlot_id = prodlot_obj.create(cr, uid, {
                        'product_id': this.product_id.id
                    }, context=context)
                    vals = {
                        'quantity': 1.0,
                        'wizard_id': this.id,
                        'wizard_exist_id': this.id,
                        'prodlot_id':prodlot_id,
                    }
                    wizard_line_obj.create(cr, uid, vals, context=context)
                    self.write(cr, uid, this.id, {
                            'qty': (this.qty - 1)
                        }, context=context)
                action['res_id'] = this.id
        action_context = {}
        if not action.get('context'):
            action_context = {}
        else:
            action_context = eval(action.get('context'))
        if context.get('active_model') == 'stock.move':
            action_context['active_model'] = 'stock.move'
            action_context['active_ids'] = context.get('active_ids')
        action['context'] = str(action_context)
        return action
    
class stock_picking_in(orm.Model):
    _inherit = 'stock.picking.in'
    
    def action_process(self, cr, uid, ids, context=None):
        split_obj = self.pool.get('stock.move.split')
        stock_move_obj = self.pool.get('stock.move')
        pick = self.browse(cr, uid, ids, context=context)
        for move_line in pick[0].move_lines:
            if move_line.product_id.track_production and not move_line.prodlot_id:
                vals = {
                    'product_id' : move_line.product_id.id,
                    'product_uom' : move_line.product_uom.id,
                    'location_id' : move_line.location_id.id,
                    'qty' : move_line.product_qty,
                }
                split_id = split_obj.create(cr, uid, vals, context=context)
                split_obj.create_prodlot(cr, uid, [split_id], context=context)
                context['active_model'] = 'stock.move'
                context['active_ids'] = [move_line.id]
                split_obj.split(cr, uid,[split_id],[move_line.id], context=context)
        ## After normal reception ##
        res = super(stock_picking_in,self).action_process(cr, uid, ids, context=context)
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: