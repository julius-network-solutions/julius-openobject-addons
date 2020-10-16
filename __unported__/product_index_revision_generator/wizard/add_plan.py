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

import base64
from openerp import models, fields, api, _


class product_add_plan(models.TransientModel):
    _name = 'product.add.plan'
    _description = 'Product add plan'

    name = fields.Char('Plan document name', required=True, default='')
    plan_document = fields.Binary(required=True)

    @api.one
    def add_plan_document(self):
        doc_obj = self.env['ir.attachment']
        product_id = self._context.get('active_id')
        if product_id:
            atts = doc_obj.search([
                                   ('res_id', '=', product_id),
                                   ('res_model', '=', 'product.product'),
                                   ('is_plan', '=', True),
                                   ], limit=1)
            vals = {
                    'is_plan': True,
                    'res_id': product_id,
                    'res_model': 'product.product',
                    'name': self.name,
                    'type': 'binary',
                    'user_id': self._uid,
                    'datas': self.plan_document,
                    }
            if atts:
                atts.write(vals)
            else:
                doc_obj.create(vals)
            product_obj = self.env['product.product']
            product = product_obj.browse(product_id)
            product.plan_revision = self.name

#     def add_plan_document(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         doc_obj = self.pool.get('ir.attachment')
#         product_id = context.get('active_id')
#         if product_id:
#             att_id = False
#             att_ids = doc_obj.search(cr, uid, [
#                 ('res_id', '=', product_id),
#                 ('res_model', '=', 'product.product'),
#                 ('is_plan', '=', True),
#                 ], context=context, limit=1)
#             if att_ids:
#                 att_id = att_ids[0]
#             rec = self.browse(cr, uid, ids[0], context=context)
#             vals = {
#                 'is_plan': True,
#                 'res_id': product_id,
#                 'res_model': 'product.product',
#                 'name': rec.name,
#                 'type': 'binary',
#                 'user_id': uid,
#                 'datas': rec.plan_document,
#             }
#             if att_id:
#                 doc_obj.write(cr, uid, att_id, vals, context=context)
#             else:
#                 doc_obj.create(cr, uid, vals, context=context)
#             self.pool.get('product.product').write(cr, uid, product_id,
#                                                    {'plan_revision': rec.name},
#                                                    context=context)
#         return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
