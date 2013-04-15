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
from openerp import netsvc
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
  
class procurement_order (orm.Model):
    _inherit = "procurement.order"
    
    def _get_newdate_value(self, cr, uid, from_dt, to_dt, date_percentage, context=None):
        delta_days = to_dt - from_dt
        diff_day = delta_days.days
        delta = diff_day * date_percentage
        newdate = from_dt + timedelta(days=delta)
        #TODO: put this part in a specific customer module
        ##############
        date_day = newdate.weekday()
        delta_d = 0
        if date_day in (0,2):
            delta_d = 1
        elif date_day not in (1,3):
            delta_d = 8 - date_day 
        newdate = newdate + timedelta(days=delta_d)
        ###############
        return newdate
    
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
                # We looking for the date_percentage defined into the product
                # If there is no percentage defined here we get the company default value
                # And if there is no value we get 2/3 as default value
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
                    'move_prod_id': res_id,
                    'company_id': procurement.company_id.id,
                })
                res[procurement.id] = produce_id
                self.write(cr, uid, [procurement.id], {'state': 'running', 'production_id': produce_id})   
                bom_result = production_obj.action_compute(cr, uid,
                        [produce_id], properties=[x.id for x in procurement.property_ids])
                wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
                if res_id:
                    stock_move_obj.write(cr, uid, [res_id], {
                            'location_id': procurement.location_id.id
                        }, context=context)
                self.production_order_create_note(cr, uid, special_ids, context=context)
                
                mo_lines = production_obj.browse(cr, uid, produce_id ,context=context).move_lines
                for mo_line in mo_lines:
                    #Move_line Manufacturing Order Date
                    stock_move_obj.write(cr, uid, mo_line.id, {
                                   'date_expected': newdate_str,
                                   'date': newdate_str,
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
            if x.location_id or x.location_id.special_location]
        if normal_ids:
            res = super(procurement_order, self).make_mo(cr, uid, normal_ids, context=None)
        if special_ids:
            res = self._special_make_mo(cr, uid, special_ids, res, context=context)
        return res
    
    def _get_purchase_order_date(self, cr, uid, procurement, company, schedule_date, context=None):
        return schedule_date
    
    def _get_purchase_schedule_date(self, cr, uid, procurement, company, context=None):
        procurement_date_planned = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        schedule_date = procurement_date_planned
        return schedule_date
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
