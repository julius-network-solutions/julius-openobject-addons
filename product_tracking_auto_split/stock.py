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
        
    def pre_split(self, cr, uid, ids, context=None):
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
#                     prodlot_id = prodlot_obj.create(cr, uid, {
#                         'product_id': this.product_id.id
#                     }, context=context)
                    vals = {
                        'quantity': 1.0,
                        'wizard_id': this.id,
                        'wizard_exist_id': this.id,
                        'prodlot_id':False,
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
    
    
    def split(self, cr, uid, ids, move_ids, context=None):
        """ To split stock moves into serial numbers
 
        :param move_ids: the ID or list of IDs of stock move we want to split
        """
        if context is None:
            context = {}
        assert context.get('active_model') == 'stock.move',\
             'Incorrect use of the stock move split wizard'
        inventory_id = context.get('inventory_id', False)
        prodlot_obj = self.pool.get('stock.production.lot')
        inventory_obj = self.pool.get('stock.inventory')
        move_obj = self.pool.get('stock.move')
        new_move = []
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                move_qty = move.product_qty
                quantity_rest = move.product_qty
                uos_qty_rest = move.product_uos_qty
                new_move = []
                if data.use_exist:
                    lines = [l for l in data.line_exist_ids if l]
                else:
                    lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
                    quantity = line.quantity
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        raise osv.except_osv(_('Processing Error!'), _('Serial number quantity %d of %s is larger than available quantity (%d)!') \
                                % (total_move_qty, move.product_id.name, move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        self.pool.get('stock.move').log(cr, uid, move.id, _('Unable to assign all lots to this move!'))
                        return False
                    default_val = {
                        'product_qty': quantity,
                        'product_uos_qty': uos_qty,
                        'state': move.state
                    }
                    if quantity_rest > 0:
                        current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                        if inventory_id and current_move:
                            inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
                        new_move.append(current_move)
 
                    if quantity_rest == 0:
                        current_move = move.id
                    prodlot_id = False
                    if data.use_exist:
                        prodlot_id = line.prodlot_id.id
#                     if not prodlot_id:
#                         prodlot_id = prodlot_obj.create(cr, uid, {
#                             'name': line.name,
#                             'product_id': move.product_id.id},
#                         context=context)
                    move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'state':move.state})
 
                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        update_val['split_in_progress'] = True
                        if quantity_rest == 1:
                            update_val['split_in_progress'] = False
                        move_obj.write(cr, uid, [move.id], update_val)
 
        return new_move
    
class stock_move(orm.Model):
    _inherit = 'stock.move'
     
    _columns = {
        'split_in_progress' : fields.boolean('Split In Progress'),            
    }
    def move_split(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        split_obj = self.pool.get('stock.move.split')
        for move in self.browse(cr, uid, ids, context=context):
            product = move.product_id
            if product.track_production and move.product_qty > 1:
                values = {
                    'product_id' : move.product_id.id,
                    'product_uom' : move.product_uom.id,
                    'location_id' : move.location_id.id,
                    'qty' : move.product_qty,
                }
                split_id = split_obj.create(cr, uid, values, context=context)
                split_obj.pre_split(cr, uid, [split_id], context=context)
                context['active_model'] = 'stock.move'
                context['active_ids'] = [move.id]
                result = split_obj.split(cr, uid, [split_id], [move.id], context=context)
        return True
     
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        res = super(stock_move, self).create(cr, uid, vals, context=context)
        if vals.get('product_qty') > 1:
            self.move_split(cr, uid, [res], context=context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        res = super(stock_move, self).write(cr, uid, ids, vals, context=context)
        if vals.get('product_qty') > 1 and vals.get('split_in_progress') == False or not vals.get('state'):
            self.move_split(cr, uid, ids, context=context)
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: