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

from openerp import models, api, fields
from openerp.tools.translate import _

class sale_order_line_make_invoice(models.TransientModel):
    _inherit = "sale.order.line.make.invoice"
    
    def make_invoices(self, cr, uid, ids, context=None):
        """
             To make invoices.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: A dictionary which of fields with values.

        """
        if context is None: context = {}
        open_invoices = context.get('open_invoices', False)
        super_context = context
        super_context['open_invoices'] = True
        res = super(sale_order_line_make_invoice, self).\
            make_invoices(cr, uid, ids, context=super_context)
        invoice_ids = res.get('res_id')
        if not isinstance(invoice_ids, list):
            invoice_ids = [invoice_ids]
        invoice_lines = {}
        sale_line_obj = self.pool.get('sale.order.line')
        invoice_line_obj = self.pool.get('account.invoice.line')
        for line in sale_line_obj.\
            browse(cr, uid, context.get('active_ids', []), context=context):
            if line.order_id.global_discount_percentage:
                discount = line.order_id.global_discount_percentage
                for invoice_line in line.invoice_lines:
                    invoice_id = invoice_line.invoice_id.id
                    if invoice_id in invoice_ids:
                        invoice_lines.setdefault(invoice_id, {})
                        invoice_lines[invoice_id].setdefault(discount, [])
                        if invoice_line.id not in \
                            invoice_lines[invoice_id][discount]:
                            invoice_lines[invoice_id][discount].\
                                append(invoice_line.id)
        if invoice_lines:
            data_obj = self.pool.get('ir.model.data')
            invoice_obj = self.pool.get('account.invoice')
            model, product_id = data_obj.\
                get_object_reference(cr, uid,
                                     'global_discount',
                                     'product_global_discount')
            for invoice_id in invoice_lines.keys():
                for discount in invoice_lines[invoice_id].keys():
                    line_ids = invoice_lines[invoice_id][discount]
                    lines = invoice_line_obj.browse(cr, uid, line_ids, context=context)
                    line_by_taxes = invoice_obj.\
                        _get_lines_by_taxes(cr, uid, invoice_id, lines, context=context)
                    invoice_ids = invoice_obj.\
                        _create_global_lines_discount_by_taxes(cr, uid, invoice_id,
                                                               line_by_taxes and line_by_taxes[0] or {},
                                                               discount,
                                                               context=context)
                    invoice_obj.\
                        button_compute(cr, uid, [invoice_id], context=context)
        if not open_invoices:
            return {'type': 'ir.actions.act_window_close'}
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
