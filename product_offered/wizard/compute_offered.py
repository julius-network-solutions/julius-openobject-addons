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

class product_compute_offered(orm.TransientModel):
    _name = "product.compute.offered"
    _description = "Generate offered Products"
    
    _columns = {
        'multiple': fields.boolean('Multiple',
            help='If checked the system will compute the offered products like this, example: '
            '- 5 products bought = 1 product offered '
            '- 10 products bought = 2 product offered, etc.'
            'else, if the customer buy 5, 10, 15 products you will only offered him 1 product'),
    }
    
    _defaults = {
        'multiple': True,
    }
    
    def _get_orders(self, cr, uid, context=None):
        if context is None:
            context = {}
        o_so = self.pool.get('sale.order')
        return o_so.search(cr, uid, [('state', '=', 'draft')], context=context)

    def do_compute_offered(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        o_so = self.pool.get('sale.order')
        sale_ids = self._get_orders(cr, uid, context=context)
        current = self.browse(cr, uid, ids[0], context=context)
        multiple = current.multiple
        o_so._generate_offered(cr, uid, sale_ids, multiple, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
