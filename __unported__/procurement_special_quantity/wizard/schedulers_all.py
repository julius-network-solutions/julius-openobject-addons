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

import threading
from openerp import pooler

from openerp.osv import fields, orm
from datetime import timedelta, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class procurement_compute_all(orm.TransientModel):
    _inherit = 'procurement.order.compute.all'

    _columns = {
        'date': fields.date('Date running', help="If you choose a date here it will recompute the procurement date taking in account this date"),
    }

    def _procure_calculation_all(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """
        if context is None:
            context = {}
        proc_obj = self.pool.get('procurement.order')
        #As this function is in a new thread, i need to open a new cursor, because the old one may be closed
        new_cr = pooler.get_db(cr.dbname).cursor()
        for proc in self.browse(new_cr, uid, ids, context=context):
            if proc.date:
                context['date_procurement_compute'] = proc.date
            else:
                context['date_procurement_compute'] = datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
            proc_obj.run_scheduler(new_cr, uid, automatic=proc.automatic, use_new_cursor=new_cr.dbname,\
                    context=context)
        #close the new cursor
        new_cr.close()
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
