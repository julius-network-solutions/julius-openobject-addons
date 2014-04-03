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
from dateutil.relativedelta import relativedelta
from openerp import netsvc
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
  
class procurement_order(orm.Model):
    _inherit = "procurement.order"
    
    def _is_special(self, cr, uid, ids, name, args, context=None):
        res = {}
        procurements = self.browse(cr, uid, ids, context=context)
        for procurement in procurements:
            res[procurement.id] = procurement.location_id.special_location
        return res
    
    def _is_special_search(self, cursor, user, obj, name, args, domain=None, context=None):
        if context is None:
            context = {}
        if not args:
            return []
        value = True
        for val in args:
            if val[0] == 'special_location':
                value = val[2]
                break
        res = []
        cursor.execute('SELECT DISTINCT(id) FROM stock_location WHERE active=True AND special_location = ' + str(value))
        res = cursor.fetchall()
        if not res:
            return [('id', '=', '0')]
        where = ""
        if res:
            val_ids = [x[0] for x in res]
            if len(val_ids) > 1:
                where = "WHERE location_id in " + str(tuple(val_ids))
            elif len(val_ids) == 1:
                where = "WHERE location_id = " + str(val_ids[0])
        request = ('SELECT DISTINCT(id) FROM procurement_order %s') %where
        cursor.execute(request)
        res = cursor.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [x[0] for x in res])]
    
    _columns = {
        'procurement_date': fields.date('Procurement date'),
        'special_location': fields.function(_is_special, fnct_search=_is_special_search, method=True, type='boolean', string='Special procurement'),
    }
    
    def _get_newdate_value(self, cr, uid, from_dt, to_dt, date_percentage, context=None):
        delta_days = to_dt - from_dt
        diff_day = delta_days.days
        delta = diff_day * date_percentage
        newdate = from_dt + timedelta(days=delta)
        return newdate
    
    def _get_date_from_procurement(self, cr, uid, procurement, context=None):
        # We looking for the date_percentage defined into the product
        # If there is no percentage defined here we get the company default value
        # And if there is no value we get 2/3 as default value
        if context is None:
            context = {}
        newdate_str = procurement.procurement_date
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        if not procurement.procurement_date:
            date_percentage = (procurement.product_id and \
                (procurement.product_id.date_percentage or \
                procurement.product_id.company_id and \
                procurement.product_id.company_id.date_percentage) \
                or company.date_percentage or (2/3 * 100)) / 100
        
            from_dt = datetime.today()
            to_dt = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
            newdate = self._get_newdate_value(cr, uid, from_dt, to_dt, date_percentage, context=context)
            res_id = procurement.move_id.id
            newdate_str = newdate.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            newdate = datetime.strptime(procurement.procurement_date, DEFAULT_SERVER_DATE_FORMAT)
            newdate_str = newdate.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return newdate_str

    def _get_purchase_date_from_procurement(self, cr, uid, procurement, context=None):
        if context is None:
            context = {}
        return procurement.date_planned

    def _get_date_done(self, cr, uid, newdate_str, procurement, context=None):
        # If we add the produce delay defined in the product,
        # We add it inside this date
        newdate_done = datetime.strptime(newdate_str, DEFAULT_SERVER_DATETIME_FORMAT) + \
            relativedelta(days=procurement.product_id.produce_delay or 0.0)
        return newdate_done.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def _special_make_mo(self, cr, uid, special_ids, res=None, context=None):
        if res is None: res = {}
        if context is None: context = {}
        if special_ids:
            company = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            procurement_obj = self.pool.get('procurement.order')
            production_obj = self.pool.get('mrp.production')
            wf_service = netsvc.LocalService("workflow")
            production_obj = self.pool.get('mrp.production')
            stock_move_obj = self.pool.get('stock.move')
            for procurement in procurement_obj.browse(cr, uid, special_ids, context=context):
                if procurement.product_qty:
                    state = procurement.move_id.state
                    res_id = procurement.move_id.id
                    # We get here the procurement date
                    newdate_str = self._get_date_from_procurement(cr, uid, procurement, context=context)
                    # Add the produce delay
                    newdate_done_str = self._get_date_done(cr, uid, newdate_str, procurement, context=context)
                    produce_id = production_obj.create(cr, uid, {
                        'origin': procurement.origin,
                        'product_id': procurement.product_id.id,
                        'product_qty': procurement.product_qty,
                        'product_uom': procurement.product_uom.id,
                        'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
                        'product_uos': procurement.product_uos and procurement.product_uos.id or False,
                        'location_src_id': procurement.location_id.id,
                        'location_dest_id': procurement.location_id.id,
                        'bom_id': procurement.bom_id and procurement.bom_id.id or False,
                        'date_planned': newdate_str,
                        'date_finished': newdate_done_str,
                        'move_prod_id': res_id,
                        'company_id': procurement.company_id.id,
                        }, context=context)
                    res[procurement.id] = produce_id
                    self.write(cr, uid, [procurement.id], {
                               'state': 'running',
                               'production_id': produce_id
                               }, context=context)   
                    bom_result = production_obj.action_compute(cr, uid,
                        [produce_id], properties = [x.id for x in procurement.property_ids])
                    wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
                    if res_id and not state == 'done':
                        stock_move_obj.write(cr, uid,
                                             [res_id], {
                                             'location_id': procurement.location_id.id,
                                             }, context=context)
                    self.production_order_create_note(cr, uid, special_ids, context=context)
                    
                    poduction = production_obj.browse(cr, uid, produce_id, context=context)
                    mo_lines = poduction.move_lines
                    for mo_line in mo_lines:
                        #Move_line Manufacturing Order Date
                        stock_move_obj.write(cr, uid,
                                             mo_line.id, {
                                             'date_expected': newdate_str,
                                             'date': newdate_str,
                                             }, context=context)
                    mo_created_lines = poduction.move_created_ids
                    date_planned = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
                    for mo_line in mo_created_lines:
                        #Move_line Manufacturing Order Date
                        stock_move_obj.write(cr, uid,
                                             mo_line.id, {
                                             'date_expected': date_planned,
                                             'date': date_planned,
                                             }, context=context)
                    production_obj.write(cr, uid,
                                         produce_id, {'date_finished': newdate_done_str},
                                         context=context)
                else:
                    self.write(cr, uid, [procurement.id], {
                               'state': 'running'
                               }, context=context)
        return res
    
    def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        if context is None: context = {}
        res = {}
        procurement_obj = self.pool.get('procurement.order')
        normal_ids = [x.id for x in procurement_obj.browse(cr, uid, ids, context=context) 
            if not x.location_id or not x.location_id.special_location]
        special_ids = [x.id for x in procurement_obj.browse(cr, uid, ids, context=context) 
            if x.location_id and x.location_id.special_location]
        if normal_ids:
            res = super(procurement_order, self).make_mo(cr, uid, normal_ids, context=None)
        if special_ids:
            res = self._special_make_mo(cr, uid, special_ids, res, context=context)
        return res

    def _special_make_po(self, cr, uid, special_ids, res=None, context=None):
        """ Make purchase order from procurement
        @return: New created Purchase Orders procurement wise
        """
        if res is None: res = {}
        if context is None: context = {}
        ids = special_ids
        if ids:
            company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
            partner_obj = self.pool.get('res.partner')
            uom_obj = self.pool.get('product.uom')
            pricelist_obj = self.pool.get('product.pricelist')
            prod_obj = self.pool.get('product.product')
            acc_pos_obj = self.pool.get('account.fiscal.position')
            seq_obj = self.pool.get('ir.sequence')
            warehouse_obj = self.pool.get('stock.warehouse')
            for procurement in self.browse(cr, uid, ids, context=context):
                if procurement.product_qty:
                    res_id = procurement.move_id.id
                    partner = procurement.product_id.seller_id # Taken Main Supplier of Product of Procurement.
                    seller_qty = procurement.product_id.seller_qty
                    partner_id = partner.id
                    address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
                    pricelist_id = partner.property_product_pricelist_purchase.id
                    warehouse_id = warehouse_obj.search(cr, uid, [('company_id', '=', procurement.company_id.id or company.id)], context=context)
                    uom_id = procurement.product_id.uom_po_id.id
        
                    qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
                    if seller_qty:
                        qty = max(qty,seller_qty)
        
                    price = pricelist_obj.price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, partner_id, {'uom': uom_id})[pricelist_id]
        
                    schedule_date = self._get_purchase_schedule_date(cr, uid, procurement, company, context=context)
                    purchase_date = self._get_purchase_order_date(cr, uid, procurement, company, schedule_date, context=context)
        
                    #Passing partner_id to context for purchase order line integrity of Line name
                    new_context = context.copy()
                    new_context.update({'lang': partner.lang, 'partner_id': partner_id})
        
                    product = prod_obj.browse(cr, uid, procurement.product_id.id, context=new_context)
                    taxes_ids = procurement.product_id.supplier_taxes_id
                    taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)
        
                    name = product.partner_ref
                    if product.description_purchase:
                        name += '\n'+ product.description_purchase
                    line_vals = {
                        'name': name,
                        'product_qty': qty,
                        'product_id': procurement.product_id.id,
                        'product_uom': uom_id,
                        'price_unit': price or 0.0,
                        'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'move_dest_id': res_id,
                        'taxes_id': [(6,0,taxes)],
                    }
                    name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % procurement.name
                    po_vals = {
                        'name': name,
                        'origin': procurement.origin,
                        'partner_id': partner_id,
                        'location_id': procurement.location_id.id,
                        'warehouse_id': warehouse_id and warehouse_id[0] or False,
                        'pricelist_id': pricelist_id,
                        'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'company_id': procurement.company_id.id,
                        'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                        'payment_term_id': partner.property_supplier_payment_term.id or False,
                    }
                    res[procurement.id] = self.create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context=new_context)
                    self.write(cr, uid, [procurement.id], {'state': 'running', 'purchase_id': res[procurement.id]})
                else:
                    self.write(cr, uid, [procurement.id], {'state': 'running'})
            self.message_post(cr, uid, ids, body=_("Draft Purchase Order created"), context=context)
        return res
    
    def make_po(self, cr, uid, ids, context=None):
        """ Make purchase order from procurement
        @return: New created Purchase Orders procurement wise
        """
        if context is None: context = {}
        res = {}
        procurement_obj = self.pool.get('procurement.order')
        normal_ids = [x.id for x in procurement_obj.browse(cr, uid, ids, context=context) 
            if not x.location_id or not x.location_id.special_location]
        special_ids = [x.id for x in procurement_obj.browse(cr, uid, ids, context=context) 
            if x.location_id and x.location_id.special_location]
        if normal_ids:
            res = super(procurement_order, self).make_po(cr, uid, normal_ids, context=None)
        if special_ids:
            res = self._special_make_po(cr, uid, special_ids, res, context=context)
        return res
    
    def _get_purchase_schedule_date(self, cr, uid, procurement, company, context=None):
        res = super(procurement_order, self)._get_purchase_schedule_date(cr, uid, procurement, company, context=context)
        if procurement.special_location:
            newdate_str = self._get_purchase_date_from_procurement(cr, uid, procurement, context=context)
            res = datetime.strptime(newdate_str, DEFAULT_SERVER_DATETIME_FORMAT)
        return res
    
    def _get_purchase_order_date(self, cr, uid, procurement, company, schedule_date, context=None):
        res = super(procurement_order, self)._get_purchase_order_date(cr, uid, procurement, company, schedule_date, context=context)
        if procurement.special_location:
            date_str = self._get_date_from_procurement(cr, uid, procurement, context=context)
            res = datetime.strptime(date_str, DEFAULT_SERVER_DATETIME_FORMAT)
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
