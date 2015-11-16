# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
###############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp import netsvc

class mrp_production(orm.Model):
    _inherit = "mrp.production"

    def __init__(self, pool, cr):
        if self._columns.get('state'):
            add_item = True
            for (a,b) in self._columns['state'].selection:
                if a == 'partially_ready':
                    add_item = False
            if add_item:
                new_selection = []
                for (a,b) in self._columns['state'].selection:
                    if a == 'ready':
                        new_selection.extend([('partially_ready',
                                               _('Partially ready'))])
                    new_selection.extend([(a,b)])
                self._columns['state'].selection = new_selection
        super(mrp_production, self).__init__(pool, cr)

    def _get_available_quantity_ready(self, cr, uid, ids,
                                      name, args, context=None):
        if context is None: context = {}
        res = {}
        move_obj = self.pool.get('stock.move')
        for prod in self.browse(cr, uid, ids, context=context):
            res[prod.id] = 0
            compo_list = {}
            if prod.state in ('confirmed', 'partially_ready'):
                available = 0
                start = True
                for component in prod.bom_id.bom_lines:
                    product_id = component.product_id.id
                    compo_list.setdefault(product_id, 0)
                    compo_list[product_id] += component.product_qty
                for move in prod.move_lines:
                    context['states_in'] = ('done',)
                    context['states_out'] = ('done', 'assigned', 'confirmed')
                    available_quantity = move_obj.\
                        _get_specific_available_qty(cr, uid, move,
                                                    context=context)
                    if available_quantity <= 0:
                        available = 0
                        break
                    component_qty = compo_list.get(move.product_id.id)
                    if component_qty == 0:
                        component_qty = 1
                    quantity = (available_quantity - \
                        (available_quantity % component_qty)) / component_qty
                    if not start:
                        available = min(quantity, available)
                    else:
                        start = False
                        available = quantity
                if available > prod.product_qty:
                    available = prod.product_qty
                res[prod.id] = available
        return res

    def _create_move_to_do(self, cr, uid, move_id,
                           quantity_to_do, context=None):
        if context is None: context = {}
        move_obj = self.pool.get('stock.move')
        new_id = move_obj.\
            copy(cr, uid, move_id, default={
                'product_qty': quantity_to_do,
                'product_uos_qty': quantity_to_do,
                'move_dest_id': False,
                }, context=context)
        return new_id

    def _write_move_to_do(self, cr, uid, move_id,
                          quantity_ready, context=None):
        if context is None: context = {}
        move_obj = self.pool.get('stock.move')
        move_obj.write(cr, uid, [move_id], {
            'product_qty': quantity_ready,
            'product_uos_qty': quantity_ready,
            }, context=context)
        return True

    def _get_quantities(self, cr, uid, production,
                        quantity_left_to_do, context=None):
        if context is None: context = {}
        quantity_ready = 0
        if not context.get('quantity_define_manually'):
            quantity_ready = production.product_qty_ready
        else:
            quantity_ready = context.get('quantity_define_manually') or 0
        quantity_to_do = quantity_left_to_do - quantity_ready
        return quantity_ready, quantity_to_do

    def partial_to_production(self, cr, uid, ids, context=None):
        if context is None: context = {}
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        qty_change_obj = self.pool.get('change.production.qty')
        procurement_obj = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        for production in self.browse(cr, uid, ids, context=context):
            if production.state not in ('partially_ready', 'ready'):
                continue
            if production.state == 'ready' and \
                not context.get('quantity_define_manually'):
                continue
            if production.state == 'partially_ready' and \
                not production.product_qty_ready:
                self.write(cr, uid, production.id,
                           {'state': 'confirmed'}, context=context)
            elif production.product_qty_ready or \
                context.get('quantity_define_manually'):
                quantity_done = 0
                for produced_product in production.move_created_ids2:
                    if (produced_product.scrapped) or \
                        (produced_product.product_id.id \
                        != production.product_id.id):
                        continue
                    quantity_done += produced_product.product_qty
                quantity_total = production.product_qty
                quantity_left_to_do = quantity_total - quantity_done
                quantity_ready, quantity_to_do = self.\
                    _get_quantities(cr, uid, production,
                                    quantity_left_to_do, context=context)
                new_move_id = False
                if quantity_to_do > 0:
                    if production.move_prod_id:
                        new_move_id = self.\
                            _create_move_to_do(cr, uid,
                                               production.move_prod_id.id,
                                               quantity_to_do, context)
                        if new_move_id:
                            move_obj.action_confirm(cr, uid, [new_move_id],
                                                    context=context)
                        self._write_move_to_do(cr, uid,
                                               production.move_prod_id.id,
                                               quantity_ready, context)

                    procurement_ids = procurement_obj.search(cr, uid, [
                        ('production_id', '=', production.id)
                        ], limit=1, context=context)
                    new_prod_id = False
                    new_procurement_id = False
                    procurement_id = False
                    if procurement_ids:
                        procurement_id = procurement_ids[0]
                        default_vals = {
                                'production_id': False,
                                'product_qty': quantity_to_do,
                            }
                        if new_move_id:
                            default_vals.update({'move_id': new_move_id,})
                        new_procurement_id = procurement_obj.\
                            copy(cr, uid, procurement_id,
                                 default=default_vals, context=context)
                        wf_service.trg_validate(uid, 'procurement.order',
                                                new_procurement_id,
                                                'button_confirm', cr)
                        wf_service.trg_validate(uid, 'procurement.order',
                                                new_procurement_id,
                                                'button_check', cr)
                        new_procurement = procurement_obj.\
                            browse(cr, uid, new_procurement_id, context=context)
                        new_prod_id = new_procurement.production_id and \
                            new_procurement.production_id.id or False
                    if not new_prod_id:
                        new_prod_id = self.copy(cr, uid,
                            production.id,
                            default={
                            'product_qty': quantity_to_do,
                            },
                            context=context)
                        vals = {
                            'sale_ref': production.sale_ref,
                            'sale_name': production.sale_name,
                        }
                        if new_move_id:
                            vals.update({'move_prod_id': new_move_id,})
                        self.write(cr, uid, new_prod_id, vals, context=context)
                        if new_procurement_id:
                            vals = {'production_id': new_prod_id,}
                            if new_move_id:
                                vals.update({'move_id': new_move_id,})
                            procurement_obj.\
                                write(cr, uid, new_procurement_id,
                                      vals, context=context)
                    wiz_id = qty_change_obj.\
                        create(cr, uid, {
                               'product_qty': quantity_ready,
                               }, context=context)
                    context_change_qty = context
                    context_change_qty.update({
                        'active_id': production.id,
                        'do_not_change_quantity': True,
                        })
                    qty_change_obj.\
                        change_prod_qty(cr, uid, [wiz_id],
                                        context=context_change_qty)
                    if procurement_id:
                        procurement_obj.\
                            write(cr, uid, procurement_id, {
                                  'product_qty': quantity_ready,
                                  }, context=context)
                    
                    self.write(cr, uid, production.id, {
                        'production_id': new_prod_id,
                        }, context=context)
#                    if production.move_prod_id:
#                        new_move_id = move_obj.copy(cr, uid, production.move_prod_id.id, default={'product_qty': quantity_to_do}, context=context)
#                        move_obj.write(cr, uid, [production.move_prod_id.id], {'product_qty': quantity_ready}, context=context)
                    wf_service.trg_validate(uid, 'mrp.production',
                                            new_prod_id,
                                            'button_confirm', cr)
                    
                    if not production.move_created_ids:
                        produce_move_id = self._make_production_produce_line(cr, uid, production, context=context)
                        for scheduled in production.product_lines:
                            self._make_production_line_procurement(cr, uid, scheduled, False, context=context)
                
                    if production.move_prod_id and production.move_prod_id.location_id.id != production.location_dest_id.id:
                        move_obj.write(cr, uid, [production.move_prod_id.id],
                                {'location_id': production.location_dest_id.id})
                    if production.picking_id:
                        picking_obj.force_assign(cr, uid, [production.picking_id.id])
                elif quantity_to_do <= 0:
                    self.force_production(cr, uid, [production.id])
            wf_service.trg_validate(uid, 'mrp.production', production.id, 'button_produce', cr)
        return True

    _columns = {
        'product_qty_ready': fields.function(_get_available_quantity_ready,
             type='float', string='Quantity ready',
             help='If you\'ve got at least the component to produce one element,' \
             'you will have a quantity here.',
             ),
        'production_id': fields.many2one('mrp.production', 'Production order to do', readonly=True),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        if not isinstance(ids, list):
            ids = [ids]
        if not vals.get('state'):
            for prod in self.browse(cr, uid, ids, context=context):
                if prod.state == 'confirmed' and prod.product_qty_ready:
                    self.write(cr, uid, [prod.id],
                               {'state': 'partially_ready'}, context=context)
                elif prod.state == 'partially_ready' and not prod.product_qty_ready:
                    self.write(cr, uid, [prod.id],
                               {'state': 'confirmed'}, context=context)
        return super(mrp_production, self).write(cr, uid, ids, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
