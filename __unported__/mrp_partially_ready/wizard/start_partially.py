# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
###############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class mrp_production_start_partially(orm.TransientModel):
    _name = "mrp.production.start.partially"
    _description = "Start partially production"

    def _get_production_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        res = False
        if context.get('active_model') == 'mrp.production':
            if context.get('active_id'):
                res = context.get('active_id')
        return res

    def _get_quantity(self, cr, uid, context=None):
        if context is None:
            context = {}
        res = 0
        if context.get('active_model') == 'mrp.production':
            if context.get('active_id'):
                production_obj = self.pool.get('mrp.production')
                prod = production_obj.\
                    read(cr, uid, context.get('active_id'),
                         ['product_qty'], context=context)
                res = prod.get('product_qty') or 0
        return res

    _columns = {
        'production_id': fields.many2one('mrp.production',
                                         'Production Order',
                                         required=True),
        'product_qty': fields.float('Quantity',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True),
    }

    _defaults = {
        'production_id': _get_production_id,
        'product_qty': _get_quantity,
    }

    def start_partially(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = True
        production_obj = self.pool.get('mrp.production')
        partial = self.browse(cr, uid, ids[0], context=context)
        production = partial.production_id
        quantity = partial.product_qty
        if quantity <= 0:
            raise orm.except_orm(_("ERROR !"),
                                 _("You can't start the production order " \
                                   "with a negative or zero quantity."))
        elif quantity > production.product_qty:
            raise orm.except_orm(_("ERROR !"),
                                 _("You can't start the production order " \
                                   "with a quantity greater " \
                                   "than %s.") % production.product_qty)
        elif quantity == production.product_qty:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrp.production',
                                    production.id, 'button_produce', cr)
            return res
        else:
            context['quantity_define_manually'] = quantity
            production_obj.partial_to_production(cr, uid,
                                                 [production.id],
                                                 context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
