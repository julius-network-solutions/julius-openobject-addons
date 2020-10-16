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
from openerp.tools import float_compare

class stock_move(orm.Model):
    _inherit = "stock.move"
    
    _columns = {
        'split_move': fields.boolean('Split move',
            help="When there is an availability check, " \
            "this action will split the move into 2 moves, " \
            "one available, and one waiting for availablity."),
    }
    
    _defaults = {
        'split_move': False,
    }
    
    def _fields_to_check(self, cr, uid, context=None):
        return [
            ('tracking_id', 'many2one'),
            ('picking_id', 'many2one'),
            ('location_id', 'many2one'),
            ('location_dest_id', 'many2one'),
            ('state', 'char'),
            ('prodlot_id', 'many2one'),
            ('product_id', 'many2one'),
            ('date_expected', 'char'),
        ]
        
    def _get_context_check(self, cr, uid,
        move, what=('in'), states=('assigned','done'), context=None):
        return {
            'shop': False,
            'warehouse': False,
            'location': move and move.location_id and \
            move.location_id.id or False,
            'states': states,
            'what': what,
        }
        
    def _get_specific_available_qty(self, cr, uid, move, context=None):
        if context is None:
            context = {}
        c = context.copy()
        available_qty = 0
        if move:
            product_obj = self.pool.get('product.product')
            what = ('in',)
            states = context.get('states')
            if not states:
                states = ('assigned', 'done')
            states_in = context.get('states_in')
            if not states_in:
                states_in = states
            states_out = context.get('states_out')
            if not states_out:
                states_out = states
            c.update(self._get_context_check(
                cr, uid, move, what=what, states=states_in, context=context))
            stock = product_obj.get_product_available(
                cr, uid, [move.product_id.id], context=c)
            incoming_qty = stock.get(move.product_id.id, 0.0)
            what = ('out',)
            c.update(self._get_context_check(
                cr, uid, move, what=what, states=states_out, context=context))
            stock = product_obj.get_product_available(
                cr, uid, [move.product_id.id], context=c)
            outgoing_qty = stock.get(move.product_id.id, 0.0)
            available_qty = incoming_qty + outgoing_qty
        return available_qty

    def _do_operations_to_merge_move(self, cr, uid,
        move_to_keep_id, ids_to_remove, context=None):
        if context is None:
            context = {}
        procurement_obj = self.pool.get('procurement.order')
        production_obj = self.pool.get('mrp.production')
        move_to_write_ids = self.search(cr, uid, [
            ('move_dest_id', 'in', ids_to_remove),
            ], context=context)
        self.write(cr, uid, move_to_write_ids, {
            'move_dest_id': move_to_keep_id,
            }, context=context)
        proc_to_write_ids = procurement_obj.search(cr, uid, [
            ('move_id', 'in', ids_to_remove),
            ], context=context)
        procurement_obj.write(cr, uid, proc_to_write_ids, {
            'move_id': move_to_keep_id,
            }, context=context)
        prod_to_write_ids = production_obj.search(cr, uid, [
            ('move_prod_id', 'in', ids_to_remove),
            ], context=context)
        production_obj.write(cr, uid, prod_to_write_ids, {
            'move_prod_id': move_to_keep_id,
            }, context=context)
        return True

    def _merge_move(self, cr, uid, move_id, context=None):
        if context is None:
            context = {}
        if self.search(cr, uid, [('id', '=', move_id)], context=context):
            move = self.browse(cr, uid, move_id, context=context)
            if move.state in \
                ('confirmed', 'waiting', 'assigned') and move.split_move:
                fields_to_check = self._fields_to_check(
                    cr, uid, context=context)
                ids_to_remove = []
                domain_search = []
                for field, ttype in fields_to_check:
                    if move[field]:
                        if ttype == 'many2one':
                            if move[field].id:
                                domain_search += [
                                    (field, '=', move[field].id),
                                ]
                            else:
                                domain_search += [
                                    (field, '=', False),
                                ]
                        elif ttype == 'char':
                            if move[field]:
                                domain_search += [
                                    (field, '=', move[field]),
                                ]
                            else:
                                domain_search += [
                                    (field, '=', False),
                                ]
                move_to_merge_ids = self.search(
                    cr, uid, domain_search, context=context)
                origin_domain = [
                    ('move_dest_id', 'in', move_to_merge_ids),
                    ('state', '!=', 'done'),
                    ]
                if move.picking_id:
                    origin_domain += [
                        ('picking_id', '!=', move.picking_id.id),
                    ]
                move_origin_ids = self.search(
                    cr, uid, origin_domain, context=context)
                move_dest_ids = [x.move_dest_id.id
                    for x in self.browse(cr, uid,
                                         move_origin_ids, context=context)
                    if x.move_dest_id]
                for move in move_dest_ids:
                    if move in move_to_merge_ids:
                        move_to_merge_ids.remove(move)
                if len(move_to_merge_ids) > 1:
                    move_to_keep_id = min(move_to_merge_ids)
                    product_qty = 0
                    product_uos_qty = 0
                    for move in self.browse(
                        cr, uid, move_to_merge_ids, context=context):
                        product_qty += move.product_qty
                        product_uos_qty += move.product_uos_qty
                        if move.id != move_to_keep_id:
                            ids_to_remove.append(move.id)
                    update_vals = {
                        'product_qty': product_qty,
                        'product_uos_qty': product_uos_qty,
                    }
                    self.write(cr, uid,
                               move_to_keep_id,
                               update_vals, context=context)
                    self.write(cr, uid, ids_to_remove,
                               {'state': 'draft'}, context=context)
                    self._do_operations_to_merge_move(
                        cr, uid, move_to_keep_id,
                        ids_to_remove, context=context)
                    self.unlink(cr, uid, ids_to_remove, context=context)
        return True
    
    def _split_move(self, cr, uid, move, context=None):
        if context is None:
            context = {}
        new_move_id = False
        context['states_in'] = ('done',)
        context['states_out'] = ('assigned', 'done',)
        available_quantity = self._get_specific_available_qty(
            cr, uid, move, context=context)
        #TODO: Get the good value for the available_uos_qty
        available_uos_qty = available_quantity
        if available_quantity and available_quantity < move.product_qty:
#            if available_quantity > 0:
#                quantity_rest = 0
#            else:
            quantity_rest = move.product_qty - available_quantity
            #TODO: Get the good value for the uos_qty_rest
#            if available_uos_qty > 0:
#                uos_qty_rest = 0
#            else:
            uos_qty_rest = move.product_uos_qty - available_uos_qty
            update_val = {
                'product_qty': move.product_qty - quantity_rest,
                'product_uos_qty': move.product_uos_qty - uos_qty_rest,
            }
            self.write(cr, uid, move.id, update_val, context=context)
            if quantity_rest:
                copy_val = {
                    'product_qty': quantity_rest,
                    'product_uos_qty': uos_qty_rest,
                    'state': move.state,
                }
                new_move_id = self.copy(
                    cr, uid, move.id, default=copy_val, context=context)
        return new_move_id
    
    def action_assign(self, cr, uid, ids, context=None):
        """ Changes state to confirmed or waiting.
        @return: List of values
        """
        if context is None:
            context = {}
        todo = []
        tomerge = []
        for move in self.browse(cr, uid, ids, context=context):
            # Split moves
            if move.state in ('confirmed', 'waiting'):
                if move.split_move:
                    new_move_id = self._split_move(
                        cr, uid, move, context=context)
                    if new_move_id:
                        tomerge.append(new_move_id)
                todo.append(move.id)
        res = self.check_assign(cr, uid, todo, context=context)
        
        # Merge moves
        for move_id in tomerge:
            self._merge_move(cr, uid, move_id, context=context)
        return res

    def cancel_assign(self, cr, uid, ids, context=None):
        """ Changes the state to confirmed.
        @return: True
        """
        
        if context is None:
            context = {}
        super(stock_move, self).cancel_assign(
            cr, uid, ids, context=context)
        for move_id in ids:
            self._merge_move(cr, uid, move_id, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
