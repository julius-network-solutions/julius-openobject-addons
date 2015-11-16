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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class split_picking(orm.TransientModel):
    _name = 'split.picking'
    
    _columns = {
#        'name': fields.char("Name", size=64),
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
    
    def get_period(self, cr, uid, period='month', context=None):
        if context is None:
            context = {}
        time_delta = relativedelta()
        if period == 'day':
            time_delta = relativedelta(days=1)
        elif period == 'week':
            time_delta = relativedelta(weeks=1)
        elif period == 'month':
            time_delta = relativedelta(months=1)
        elif period == 'year':
            time_delta = relativedelta(years=1)
        return time_delta
        
    def split_picking(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids[0], context=context)
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        origin_number = data.get('number') or 0
        if origin_number <= 0:
            raise orm.except_orm(_("Warning"),
                    _('Please inform a quantity (upper than 0)'))
        period = data.get('period') or 'month'
        picking_ids = context.get('active_ids') or []
        for picking in picking_obj.browse(cr, uid, picking_ids, context=context):
            number = origin_number
            if picking.state in ('cancel','done'):
                raise orm.except_orm(_("Warning"),
                        _('This picking is not in the proper state'))
            lines_qty = {}
            delta = self.get_period(cr, uid, period, context=context)
            date = datetime.strptime(picking.date,
                            DEFAULT_SERVER_DATETIME_FORMAT)
            min_date = datetime.strptime(picking.min_date,
                            DEFAULT_SERVER_DATETIME_FORMAT)
            for line in picking.move_lines:
                new_line_qty = line.product_qty / number
                lines_qty[line.product_id.id] = {
                    'quantity': int(new_line_qty),
                    'rounding': new_line_qty - int(new_line_qty),
                }
            while number > 0:
                if number != origin_number:
                    date += delta
                    min_date += delta
                format_date = datetime.strftime(date,
                                DEFAULT_SERVER_DATETIME_FORMAT)
                format_min_date = datetime.strftime(min_date,
                                DEFAULT_SERVER_DATETIME_FORMAT)
                default = {
                    'date': format_date,
                    'min_date': format_min_date,
                }
                new_picking_id = picking_obj.copy(cr, uid,
                        picking.id, default=default, context=context)
                new_picking = picking_obj.browse(cr, uid,
                                    new_picking_id, context=context)
                for line in new_picking.move_lines:
                    qty = lines_qty[line.product_id.id].get('quantity') or 0
                    if number == 1:
                        rounding = lines_qty[line.product_id.id].get('rounding') or 0
                        qty += rounding * origin_number
                    move_obj.write(cr, uid, line.id, {
                            'product_qty': qty,
                            'date': format_date,
                            'date_expected': format_min_date,
                        }, context=context)
                picking_obj.write(cr, uid, new_picking_id, {
                            'min_date': format_min_date,
                            'origin': picking.origin,
                        }, context=context)
                number -= 1
                picking_obj.draft_force_assign(cr, uid, [new_picking_id], context)
            picking_obj.action_cancel(cr, uid, [picking.id], context=context)
        return {
            'type': 'ir.actions.act_window_close'
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
