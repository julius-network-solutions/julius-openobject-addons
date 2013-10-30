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

from openerp.osv import orm, fields
from openerp.tools.translate import _

class product_supplierinfo(orm.Model):
    _inherit = 'product.supplierinfo'

    _columns = {
        'product_variant_id': fields.many2one('product.product', 'Variant Product'),
    }

    def onchange_variant(self, cr, uid, ids, product_variant_id, context=None):
        if context is None:
            context = {}
        res = {'value': {'product_id': False}}
        if product_variant_id:
            product_obj = self.pool.get('product.product')
            product = product_obj.read(cr, uid, product_variant_id, ['product_tmpl_id'], context=context)
            product_id = product.get('product_tmpl_id') and product['product_tmpl_id'][0] or False
            if product_id:
                res['value']['product_id'] = product_id
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
