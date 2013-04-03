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
import time
from datetime import datetime, timedelta ,date
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv, orm
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

 
  
class procurement_order (orm.Model):
    _inherit = "procurement.order"
    
    def make_mo(self, cr, uid, ids, context=None):
        res = super(procurement_order, self).make_mo(cr, uid, ids, context=None)
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        production_obj = self.pool.get('mrp.production')
        product_obj = self.pool.get('product.product')
        stock_move_obj = self.pool.get('stock.move')
        for procurement_id in res:
            procurement = self.browse(cr, uid, procurement_id, context=context)
            date_percentage = product_obj.browse(cr, uid, procurement.product_id.id, context=context).date_percentage

            from_dt = datetime.today()
            to_dt = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
            delta_days = to_dt - from_dt
            diff_day = delta_days.days
            delta = diff_day * date_percentage
            date = from_dt + timedelta(days=delta)
            
            #Manufacturing Order Date
            
            production_obj.write(cr, uid, res[procurement_id], {'date_planned': date}, context=context)
            production_data = production_obj.browse(cr, uid, res[procurement_id], context=context)
            
            mo_lines = production_data.move_lines
            for mo_line in mo_lines:
                #Move_line Manufacturing Order Date
                stock_move_obj.write(cr, uid, mo_line.id, {
                                                           'date_expected': date,
                                                           'date': date
                                                           }, context=context)
            
#                procurement_child = self.search(cr, uid, [('move_id','=',mo_line.id)], limit=1, context=context)
#                print procurement_child 
#                self.write(cr, uid, procurement_child.id, {'date_planned': date}, context=context)
        return res



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: