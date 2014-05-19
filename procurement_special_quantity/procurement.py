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
from openerp import pooler
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class procurement_order(orm.Model):
    _inherit = "procurement.order"
    
    _order = 'priority desc,date_planned,origin'
    
    _columns = {
        'parent_procurement_id': fields.many2one('procurement.order', 'Parent procurement'),
        'linked_procurement_ids': fields.many2one('procurement.order', 'parent_procurement_id', 'Linked procurements'),
    }

    def _get_quantity_to_make(self, cr, uid, to_buy,
                              procurement, move_qty,
                              product_available_qty,
                              context=None):
        if context is None:
            context = {}
        quantity_to_make = 0
        if to_buy:
            if product_available_qty < 0:
                quantity_to_make = abs(min(move_qty, product_available_qty))
            else:
                if product_available_qty >= move_qty:
                    quantity_to_make = 0
                else:
                    quantity_to_make = move_qty - product_available_qty
        else:
            if (move_qty + product_available_qty) >= 0:
                # If we've got enough products we don't need
                # to procure new products
                if product_available_qty > 0:
                    # If the available quantity is positive
                    # this means that we don't need
                    # to procure any product
                    quantity_to_make = 0
                else:
                    # If negative, we have to get
                    # the minimum quantity between
                    # the move quantity and available quantity
                    quantity_to_make = abs(min(move_qty, product_available_qty))
            else:
                quantity_to_make = move_qty
        return quantity_to_make

    def button_check_quantity_to_make(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        special_ids = []
        move_obj = self.pool.get('stock.move')
        company_obj = self.pool.get('res.company')
        wf_service = netsvc.LocalService("workflow")
        res = []
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.parent_procurement_id:
                procurement = procurement.parent_procurement_id
            to_buy = False
            if procurement.product_id.supply_method == 'buy':
                to_buy = True
            if procurement.special_location:
                c = context.copy()
                c.update({
                    'states': ('confirmed','waiting','assigned'),
#                    'states_in': ('confirmed','waiting','assigned','done'),
#                    'state_out': ('assigned','done'),
                    'to_date': procurement.date_planned,
                })
                # This is the move quantity
                move_qty = procurement.move_id.product_qty or 0
                # We get here the total of pieces available at the wanted date
                product_available_qty = move_obj._get_specific_available_qty(cr, uid, procurement.move_id, context=c)
                c.update({
                    'states': ('done',),
                    'to_date': False,
                })
                # We get here the total of pieces available for real now
                product_available_qty += move_obj._get_specific_available_qty(cr, uid, procurement.move_id, context=c)
#                if to_buy:
#                    if product_available_qty < 0:
#                        quantity_to_make = abs(min(move_qty, product_available_qty))
#                    else:
#                        if product_available_qty >= move_qty:
#                            quantity_to_make = 0
#                        else:
#                            quantity_to_make = move_qty - product_available_qty
#                else:
                if to_buy:
                    # We get here the quantity of bought quantity
                    # which have not been validated yet
                    order_line_obj = self.pool.get('purchase.order.line')
                    line_ids = order_line_obj.search(cr, uid, [
                         ('product_id', '=', procurement.product_id.id),
                         ('state', 'in', ('draft','confirmed')),
                         ('order_id.state', 'in', ('draft','sent','confirmed','approved','except_picking','except_invoice')),
                         ('move_dest_id.state', 'not in', ('cancel', 'done')),
                         ('move_dest_id.location_dest_id', '=', procurement.location_id.id),
                         ('date_planned', '<=', procurement.date_planned),
                         ], context=context)
                    bought_quantity = reduce(lambda x,y: x+y, [z.product_qty for z in order_line_obj.browse(cr, uid, line_ids, context=context)], 0)
                    product_available_qty += bought_quantity
                quantity_to_make = self._get_quantity_to_make(cr, uid, to_buy,
                    procurement, move_qty, product_available_qty, context=context)
#                if (move_qty + product_available_qty) >= 0:
#                    # If we've got enough products we don't need
#                    # to procure new products
#                    if product_available_qty > 0:
#                        # If the available quantity is positive
#                        # this means that we don't need
#                        # to procure any product
#                        quantity_to_make = 0
#                    else:
#                        # If negative, we have to get
#                        # the minimum quantity between
#                        # the move quantity and available quantity
#                        quantity_to_make = abs(min(move_qty, product_available_qty))
#                else:
#                    quantity_to_make = move_qty
##                    if bought_quantity > 0:
##                        # We remove the bought quantity
##                        # to the quantity to get
##                        quantity_to_make -= bought_quantity
##                        quantity_to_make = min(move_qty, quantity_to_make)
##                        if quantity_to_make < 0:
##                            quantity_to_make = 0
                if procurement.state in ('draft','exception','confirmed'):
                    write_vals = {
                        'product_qty': quantity_to_make,
                        'product_uos_qty': quantity_to_make,
                    }
                    self.write(cr, uid, procurement.id, write_vals, context=context)
                    if procurement.id not in res:
                        res.append(procurement.id)
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
                                    if linked.id not in res:
                                        res.append(linked.id)
                                    break
                        if copy_procurement:
                            if quantity_to_make > 0:
                                default = {
                                    'product_qty': quantity_to_make,
                                    'product_uos_qty': quantity_to_make,
                                    'parent_procurement_id': procurement.id,
                                }
                                if context.get('date_procurement_compute') \
                                    and procurement.procurement_date:
                                    from_dt = datetime.strptime(context.get('date_procurement_compute'),
                                                                DEFAULT_SERVER_DATE_FORMAT)
                                    to_dt = datetime.strptime(procurement.date_planned,
                                                              DEFAULT_SERVER_DATETIME_FORMAT)
                                    date_percentage = (procurement.product_id and \
                                        (procurement.product_id.date_percentage or \
                                        procurement.product_id.company_id and \
                                        procurement.product_id.company_id.date_percentage)) or False
                                    if not date_percentage:
                                        company = company_obj.\
                                            _company_default_get(cr, uid, context=context) \
                                            or False
                                        date_percentage = company.date_percentage or (2/3 * 100) / 100
                                    procurement_date = self._get_newdate_value(cr, uid, from_dt, to_dt, date_percentage, context=context)
                                    procurement_date = procurement_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                                    default = {
                                        'procurement_date': procurement_date,
                                    }
                                new_id = self.copy(cr, uid, procurement.id, default=default, context=context)
                                wf_service.trg_validate(uid, 'procurement.order', new_id, 'button_confirm', cr)
                                res.append(new_id)
        return res
    
    def _procure_confirm(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        '''
        Call the scheduler to check the procurement order

        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param uid: The current user ID for security checks
        @param ids: List of selected IDs
        @param use_new_cursor: False or the dbname
        @param context: A standard dictionary for contextual values
        @return:  Dictionary of values
        '''
        if context is None:
            context = {}
        try:
            if use_new_cursor:
                cr = pooler.get_db(use_new_cursor).cursor()
            wf_service = netsvc.LocalService("workflow")

            procurement_obj = self.pool.get('procurement.order')
            if not ids:
                ids = procurement_obj.search(cr, uid, [('state', '=', 'exception')], order="date_planned")
            for id in ids:
                wf_service.trg_validate(uid, 'procurement.order', id, 'button_restart', cr)
            if use_new_cursor:
                cr.commit()
            company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
            maxdate = (datetime.today() + relativedelta(days=company.schedule_range)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
            start_date = fields.datetime.now()
            offset_produce = 0
            offset_buy = 0
            offset_special_produce = 0
            offset_special_buy = 0
            report = []
            report_total = 0
            report_except = 0
            report_later = 0
            while True:
                produce_ids = procurement_obj.search(cr, uid, [
                    ('state', '=', 'confirmed'),
                    ('procure_method', '=', 'make_to_order'),
                    ('product_id.supply_method', '=', 'produce'),
                    ], offset=offset_produce, limit=500, order='priority, move_id, date_planned', context=context)
                for proc in procurement_obj.browse(cr, uid, produce_ids, context=context):
                    if maxdate >= proc.date_planned:
                        wf_service.trg_validate(uid, 'procurement.order', proc.id, 'button_check', cr)
                    else:
                        offset_produce += 1
                        report_later += 1

                    if proc.state == 'exception':
                        report.append(_('PROC %d: on order - %3.2f %-5s - %s') % \
                                (proc.id, proc.product_qty, proc.product_uom.name,
                                    proc.product_id.name))
                        report_except += 1
                    report_total += 1
                if use_new_cursor:
                    cr.commit()
                special_produce_ids = procurement_obj.search(cr, uid, [
                    ('state', '=', 'running'),
                    ('procure_method', '=', 'make_to_order'),
                    ('product_id.supply_method', '=', 'produce'),
                    ('location_id.special_location', '=', True),
                    ], offset=offset_special_produce, limit=500, order='priority, move_id, date_planned, origin', context=context)
                for proc in procurement_obj.browse(cr, uid, special_produce_ids, context=context):
                    to_confirm_ids = procurement_obj.button_check_quantity_to_make(cr, uid, [proc.id], context=context)
                    for proc in procurement_obj.browse(cr, uid, to_confirm_ids, context=context):
                        wf_service.trg_validate(uid, 'procurement.order', proc.id, 'button_check', cr)
                        if proc.state == 'exception':
                            report.append(_('PROC %d: on order - %3.2f %-5s - %s') % \
                                    (proc.id, proc.product_qty, proc.product_uom.name,
                                        proc.product_id.name))
                            report_except += 1
                        report_total += 1
                    offset_special_produce += 1
                buy_ids = procurement_obj.search(cr, uid, [
                    ('state', '=', 'confirmed'),
                    ('procure_method', '=', 'make_to_order'), 
                    ('product_id.supply_method', '=', 'buy'),
                    ], offset=offset_buy, limit=500, order='priority, move_id, date_planned', context=context)
                for proc in procurement_obj.browse(cr, uid, buy_ids, context=context):
                    if maxdate >= proc.date_planned:
                        wf_service.trg_validate(uid, 'procurement.order', proc.id, 'button_check', cr)
                    else:
                        offset_buy += 1
                        report_later += 1

                    if proc.state == 'exception':
                        report.append(_('PROC %d: on order - %3.2f %-5s - %s') % \
                                (proc.id, proc.product_qty, proc.product_uom.name,
                                    proc.product_id.name))
                        report_except += 1
                    report_total += 1
                if use_new_cursor:
                    cr.commit()
                special_buy_ids = procurement_obj.search(cr, uid, [
                    ('state', '=', 'running'),
                    ('procure_method', '=', 'make_to_order'),
                    ('product_id.supply_method', '=', 'buy'),
                    ('location_id.special_location', '=', True),
                    ], offset=offset_special_buy, limit=500, order='priority, move_id, date_planned, origin', context=context)
                for proc in procurement_obj.browse(cr, uid, special_buy_ids, context=context):
                    to_confirm_ids = procurement_obj.button_check_quantity_to_make(cr, uid, [proc.id], context=context)
                    for proc in procurement_obj.browse(cr, uid, to_confirm_ids, context=context):
                        wf_service.trg_validate(uid, 'procurement.order', proc.id, 'button_check', cr)
                        if proc.state == 'exception':
                            report.append(_('PROC %d: on order - %3.2f %-5s - %s') % \
                                    (proc.id, proc.product_qty, proc.product_uom.name,
                                        proc.product_id.name))
                            report_except += 1
                        report_total += 1
                    offset_special_buy += 1
                if use_new_cursor:
                    cr.commit()
                if not produce_ids and not buy_ids and not special_buy_ids and not special_produce_ids:
                    break
            offset = 0
            ids = []
            while True:
                report_ids = []
                
                for proc in procurement_obj.browse(cr, uid, ids):
                    if maxdate >= proc.date_planned:
                        wf_service.trg_validate(uid, 'procurement.order', proc.id, 'button_check', cr)
                        report_ids.append(proc.id)
                    else:
                        report_later += 1
                    report_total += 1

                    if proc.state == 'exception':
                        report.append(_('PROC %d: from stock - %3.2f %-5s - %s') % \
                                (proc.id, proc.product_qty, proc.product_uom.name,
                                    proc.product_id.name,))
                        report_except += 1


                if use_new_cursor:
                    cr.commit()
                offset += len(ids)
                if not ids: break
            end_date = fields.datetime.now()

            if use_new_cursor:
                cr.commit()
            ids = procurement_obj.search(cr, uid, [
                ('state', '=', 'running'),
                ('move_id.state', '=', 'done'),
                ('product_qty', '=', 0)])
            procurement_obj.write(cr, uid, ids, {'state': 'done'})
            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return {}

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
