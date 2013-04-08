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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class split_picking(orm.TransientModel):
    _name = 'split.picking'
    
    _columns = {
        'name': fields.char("Name", size=64),
        'number': fields.integer("Number"),
        'period': fields.selection([
                ('day','Day'),
                ('week','Week'),
                ('month','Month'),
                ('year','Year'),
            ], 'Period'),
    }

    _defaults = {
        'number': 1.0,
        'period': 'month',
    }
    
    def get_period(self, cr, uid, period, context=None):
        if context is None:
            context = {}
        if period == 'day':
            time_delta = timedelta(days=1)
        elif period == 'week':
            time_delta = timedelta(days=7)
        elif period == 'month':
            time_delta = relativedelta(months=1)
        elif period == 'year':
            time_delta = relativedelta(months=12)
        return time_delta
        
    def split_picking(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids[0])
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        for picking in picking_obj.browse(cr, uid, context.get('active_ids'), context=context):
            if picking.state == 'done' or picking.state == 'cancel':
                raise osv.except_osv(_("Warning"), _('This picking is not in the proper state'))
            lines_qty = {}
            number = data.get('number')
            timedelta = self.get_period(cr, uid, data.get('period'), context=context)
            date = datetime.strptime(picking.date, DEFAULT_SERVER_DATETIME_FORMAT)
            min_date = datetime.strptime(picking.min_date, DEFAULT_SERVER_DATETIME_FORMAT)
            for line in picking.move_lines:
                new_line_qty = line.product_qty / data.get('number')
                lines_qty[line.product_id.id] = {
                    'quantity': int(new_line_qty),
                    'rounding': new_line_qty - int(new_line_qty),
                }
            while number > 0:
                date += timedelta
                min_date += timedelta
                default = {
                    'date': datetime.strftime(date, DEFAULT_SERVER_DATETIME_FORMAT),
                    'min_date': datetime.strftime(min_date, DEFAULT_SERVER_DATETIME_FORMAT),
                }
                new_picking_id = picking_obj.copy(cr, uid, picking.id, default=default, context=context)
                new_picking = picking_obj.browse(cr, uid, new_picking_id, context=context)
                for line in new_picking.move_lines:
                    qty = lines_qty[line.product_id.id].get('quantity')
                    if number == 1:
                        qty += lines_qty[line.product_id.id].get('rounding') * data.get('number')
                    move_obj.write(cr, uid, line.id, {
                            'product_qty': qty,
                            'date': datetime.strftime(date, DEFAULT_SERVER_DATETIME_FORMAT),
                            'date_expected': datetime.strftime(date, DEFAULT_SERVER_DATETIME_FORMAT),
                        }, context=context)
                picking_obj.write(cr, uid, new_picking_id, {'min_date':datetime.strftime(min_date, DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
                number -= 1
            picking_obj.write(cr, uid, picking.id, {'state':'cancel'}, context=context)
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: