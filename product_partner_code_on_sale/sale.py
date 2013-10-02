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

class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    
    def _get_product_partner_code(self, cr, uid, ids,
                                  name, args, context=None):
        if context is None:
            context = {}
        res = {}
        product_partner_code_obj = self.pool.get('product.partner.code')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = ''
            partner = line.order_id.partner_id
            product = line.product_id
            if product and partner:
                code_ids = product_partner_code_obj.search(cr, uid, [
                    ('product_id', '=', product.id),
                    ('partner_id', '=', partner.id),
                    ], limit=1, context=context)
                if code_ids:
                    code = product_partner_code_obj.browse(cr, uid,
                        code_ids[0], context=context).code or ''
                    res[line.id] = code
        return res
    
    _columns = {
        'product_partner_code': fields.function(_get_product_partner_code,
            string='Product Partner Code', type='char', size=64),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
