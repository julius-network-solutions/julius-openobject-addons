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
from openerp import netsvc

class procurement_order(orm.Model):
    _inherit = "procurement.order"
    
    _columns = {
        'parent_procurement_id': fields.many2one('procurement.order', 'Parent procurement'),
        'linked_procurement_ids': fields.many2one('procurement.order', 'parent_procurement_id', 'Linked procurements'),
    }
    
    def button_check_quantity_to_make(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        special_ids = []
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.parent_procurement_id:
                procurement = procurement.parent_procurement_id
            if procurement.special_location:
                c = context.copy()
                c.update({
                    'states': ('confirmed','waiting','assigned','done'),
#                        'states_in': ('confirmed','waiting','assigned','done'),
#                        'state_out': ('assigned','done'),
                    'to_date': procurement.date_planned,
                })
                # This is the move quantity
                move_qty = procurement.move_id.product_qty
                # We get here the total of pieces available
                product_available_qty = move_obj._get_specific_available_qty(cr, uid, procurement.move_id, context=c)
                if product_available_qty < 0:
                    quantity_to_make = min(move_qty, -product_available_qty)
                else:
                    quantity_to_make = min(move_qty, product_available_qty)
                if procurement.state in ('draft','exception','confirmed'):
                    write_vals = {
                        'product_qty': quantity_to_make,
                        'product_uos_qty': quantity_to_make,
                    }
                    self.write(cr, uid, procurement.id, write_vals, context=context)
                elif procurement.state in ('running', 'ready', 'waiting'):
                    if product_available_qty < 0 and quantity_to_make > 0:
                        copy_procurement = context.get('copy_child') or True
                        linked_procurement_ids = self.search(cr, uid, [
                                ('parent_procurement_id', '=', procurement.id)
                            ], context=context)
                        linked_qty = 0
                        if linked_procurement_ids:
                            for linked in self.browse(cr, uid, linked_procurement_ids, context=context):
                                if linked.state in ('draft', 'exception', 'confirmed'):
                                    self.write(cr, uid, linked.id, {
                                                'product_qty': quantity_to_make,
                                                'product_uos_qty': quantity_to_make,
                                            }, context=context)
                                    copy_procurement = False
                                    break
                        if copy_procurement:
                            if quantity_to_make > 0:
                                new_id = self.copy(cr, uid, procurement.id, default={
                                            'product_qty': quantity_to_make,
                                            'product_uos_qty': quantity_to_make,
                                            'parent_procurement_id': procurement.id,
                                        }, context=context)
                                wf_service.trg_validate(uid, 'procurement.order', new_id, 'button_confirm', cr)
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
