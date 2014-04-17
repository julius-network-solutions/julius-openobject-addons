# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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

class change_production_qty(orm.TransientModel):
    _inherit = 'change.production.qty'

    def change_prod_qty(self, cr, uid, ids, context=None):
        """
        Changes the Quantity of Product.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        if context is None: context = {}
        if context.get('do_not_change_quantity'):
            record_id = context and context.get('active_id',False)
            assert record_id, _('Active Id not found')
            prod_obj = self.pool.get('mrp.production')
            move_obj = self.pool.get('stock.move')
            data = {}
            for wiz_qty in self.browse(cr, uid, ids, context=context):
                prod = prod_obj.browse(cr, uid, record_id, context=context)
                if not prod.id in data.keys() and prod.move_prod_id:
                    data[prod.id] = (prod.move_prod_id.id, prod.move_prod_id.product_qty)
        res = super(change_production_qty, self).change_prod_qty(cr, uid, ids, context=context)
        if context.get('do_not_change_quantity'):
            for prod_id in data.keys():
                move_id, product_qty = data[prod_id]
                if move_id:
                    move_obj.write(cr, uid, move_id, {'product_qty': product_qty})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
