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
    
    def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        production_obj = self.pool.get('mrp.production')
        wf_service = netsvc.LocalService("workflow")
        procurement_obj = self.pool.get('procurement.order')
        production_obj = self.pool.get('mrp.production')
        stock_move_obj = self.pool.get('stock.move')
        
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            if procurement.location_id.special_location == False:
                res = super(procurement_order, self).make_mo(cr, uid, ids, context=None)
            elif procurement.location_id.special_location == True:
                # We looking for the date_percentage defined into the product
                # If there is no percentage defined here we get the company default value
                # And if there is no value we get 2/3 as default value
                date_percentage = procurement.product_id.date_percentage
                from_dt = datetime.today()
                to_dt = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
                delta_days = to_dt - from_dt
                diff_day = delta_days.days
                delta = diff_day * date_percentage
                date = from_dt + timedelta(days=delta)
                res_id = procurement.move_id.id
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
                    'date_planned': date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'move_prod_id': res_id,
                    'company_id': procurement.company_id.id,
                })
                res[procurement.id] = produce_id
                self.write(cr, uid, [procurement.id], {'state': 'running', 'production_id': produce_id})   
                bom_result = production_obj.action_compute(cr, uid,
                        [produce_id], properties=[x.id for x in procurement.property_ids])
                wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
                if res_id:
                    stock_move_obj.write(cr, uid, [res_id],
                            {'location_id': procurement.location_id.id})
                self.production_order_create_note(cr, uid, ids, context=context)
                
                mo_lines = production_obj.browse(cr,uid,produce_id ,context=context).move_lines
                for mo_line in mo_lines:
                    #Move_line Manufacturing Order Date
                    stock_move_obj.write(cr, uid, mo_line.id, {
                                   'date_expected': date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                   'date': date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                               }, context=context)
            
        return res
    
    def _get_purchase_order_date(self, cr, uid, procurement, company, schedule_date, context=None):
        return schedule_date
    def _get_purchase_schedule_date(self, cr, uid, procurement, company, context=None):
        procurement_date_planned = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        schedule_date = procurement_date_planned
        return schedule_date
#class mrp_production(orm.Model):
#    _inherit = 'mrp.production'
#    
#    def _make_production_line_procurement(self, cr, uid, production_line, shipment_move_id, context=None):
#        print production_line
#        print shipment_move_id
#        res = super(mrp_production, self)._make_production_line_procurement(cr, uid, production_line, shipment_move_id, context=context)
#        sale_order_obj = self.pool.get('sale.order')
#        procurement_order_obj = self.pool.get('procurement.order')
#        stock_move_obj = self.pool.get('stock.move')
#        production = production_line.production_id
#        date = stock_move_obj.browse(cr,uid,shipment_move_id,context=context).date_expected
#        print date
#        procurement_order_obj.write(cr, uid, res,{'date_planned': date}, context=context)
#        print lol
#        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: