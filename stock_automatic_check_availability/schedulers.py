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
from openerp import pooler

class stock_picking(orm.Model):
    _inherit = "stock.picking"
    
    def run_check_scheduler(self, cr, uid,
                    use_new_cursor=False, context=None):
        ''' Runs through scheduler.
        @param use_new_cursor: False or the dbname
        '''
        self._check_availability_order_by_date(cr, uid, \
                use_new_cursor=use_new_cursor, context=context)
        return True
        
    def _check_move_list_assign(self, cr, uid, move_ids, picking_ids, context=None):
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        for move_id in move_ids:
            move_obj.action_assign(cr, uid, [move_id], context)
        return True
    
    def _get_picking_domain_for_auto_check(self, cr, uid, context=None):
        return [
            ('state', 'in', ['confirmed','assigned']),
            ('type', '=', 'out'),
        ]
    
    def _get_move_domain_for_auto_check(self, cr, uid, context=None):
        return []
        
    def _check_availability_order_by_date(self, cr, uid, \
                use_new_cursor=False, context=None):
        '''
        Create procurement based on Orderpoint
        use_new_cursor: False or the dbname

        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param user_id: The current user ID for security checks
        @param context: A standard dictionary for contextual values
        @param param: False or the dbname
        @return:  Dictionary of values
        """
        '''
        if context is None:
            context = {}
        if use_new_cursor:
            cr = pooler.get_db(use_new_cursor).cursor()
        move_obj = self.pool.get('stock.move')
        # Looking for all picking which are to be treated
        picking_search_domain = self._get_picking_domain_for_auto_check(
                                                    cr, uid, context=context)
        picking_ids = self.search(cr, uid,
                         picking_search_domain, context=context)
        # Get the list of all move to check
        move_search_domain = self._get_move_domain_for_auto_check(
                                                    cr, uid, context=context)
        move_search_domain += [
            ('picking_id', 'in', picking_ids)
        ]
        move_ids = move_obj.search(cr, uid,
                    move_search_domain, order='date_expected', context=context)
        # Go through the move assign function
        self._check_move_list_assign(cr, uid, move_ids, picking_ids, context=context)
        if use_new_cursor:
            cr.commit()
            cr.close()
        return {}
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
