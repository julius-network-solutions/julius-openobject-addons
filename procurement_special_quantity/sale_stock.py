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
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, orm
from openerp import netsvc
from openerp.tools.translate import _
#import pytz
#from openerp import SUPERUSER_ID

class sale_order(orm.Model):
    _inherit = "sale.order"
    
    #TODO check how to work if the procurement line = 0
    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, context=None):
        if context is None:
            context = {}
        res = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context)
        move_obj = self.pool.get('stock.move')
        if move_id:
            move = move_obj.browse(cr, uid, move_id, context=context)
            if move.location_id.special_location:
                c = context.copy()
                c.update({
                    'states': ('confirmed','waiting','assigned'),
#                    'states_in': ('confirmed','waiting','assigned','done'),
#                    'state_out': ('assigned','done'),
                    'to_date': procurement.date_planned,
                })
                product_available_qty = move_obj._get_specific_available_qty(cr, uid, move, context=c)
                # We get here the total of pieces available at the wanted date
                c.update({
                    'states': ('done',),
                    'to_date': False,
                })
                # We get here the total of pieces available for real now
                product_available_qty += move_obj._get_specific_available_qty(cr, uid, move, context=c)
                if res.get('product_qty'):
                    product_qty = res.get('product_qty') - product_available_qty
                    if product_qty > 0:
                        res['product_qty'] = product_qty
                        #TODO get the good value here
                        res['product_uos_qty'] = product_qty
                    else:
                        res['product_qty'] = 0
                        res['product_uos_qty'] = 0
        return res
#            {
#            'name': line.name,
#            'origin': order.name,
#            'date_planned': date_planned,
#            'product_id': line.product_id.id,
#            'product_qty': line.product_uom_qty,
#            'product_uom': line.product_uom.id,
#            'product_uos_qty': (line.product_uos and line.product_uos_qty)\
#                    or line.product_uom_qty,
#            'product_uos': (line.product_uos and line.product_uos.id)\
#                    or line.product_uom.id,
#            'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
#            'procure_method': line.type,
#            'move_id': move_id,
#            'company_id': order.company_id.id,
#            'note': line.name,
#        }
class procurement_order(orm.Model):
    _inherit = "procurement.order"
    
    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms procurement and writes exception message if any.
        @return: True
        """
        normal_ids = []
        special_ids = []
        move_obj = self.pool.get('stock.move')
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.location_id.special_location:
                special_ids.append(procurement.id)
            else:
                normal_ids.append(procurement.id)
        for procurement in self.browse(cr, uid, special_ids, context=context):
            if procurement.product_id.type in ('product', 'consu'):
                if not procurement.move_id:
                    source = procurement.location_id.id
                    if procurement.procure_method == 'make_to_order':
                        source = procurement.product_id.property_stock_procurement.id
                    id = move_obj.create(cr, uid, {
                        'name': procurement.name,
                        'location_id': source,
                        'location_dest_id': procurement.location_id.id,
                        'product_id': procurement.product_id.id,
                        'product_qty': procurement.product_qty,
                        'product_uom': procurement.product_uom.id,
                        'date_expected': procurement.date_planned,
                        'state': 'draft',
                        'company_id': procurement.company_id.id,
                        'auto_validate': True,
                    })
                    move_obj.action_confirm(cr, uid, [id], context=context)
                    self.write(cr, uid, [procurement.id], {'move_id': id, 'close_move': 1})
        if special_ids:
            self.write(cr, uid, special_ids, {'state': 'confirmed', 'message': ''})
        if normal_ids:
            return super(procurement_order, self).action_confirm(cr, uid, normal_ids, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
