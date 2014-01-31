# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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

    
class account_invoice(orm.Model):
    _inherit = "account.invoice"
    
    def generate_emergency_costs_invoice_line(self, cr, uid, ids, context=None):
        invoice_line_obj = self.pool.get('account.invoice.line')
        sale_line_obj = self.pool.get('sale.order.line')
        data_obj = self.pool.get('ir.model.data')
        sale_obj = self.pool.get('sale.order')
        value = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            invoice_lines = invoice.invoice_line
            for invoice_line in invoice_lines:
                sale_line_ids = sale_line_obj.search(cr, uid, [('order_id.name','=',invoice_line.origin), ('product_id','=',invoice_line.product_id.id)],context=context)
                for sale_line in sale_line_obj.browse(cr, uid, sale_line_ids, context=context):
                    sale_order = sale_obj.browse(cr, uid, sale_line.order_id.id,context=context)
                    if sale_line.emergency_costs != 0 and not sale_line.emergency_costs_generated:
                        data_obj = self.pool.get('ir.model.data')
                        model, product_id = data_obj.get_object_reference(cr, uid, 'emergency_costs', 'product_emergency_costs')
                        res = sale_line_obj.product_id_change(cr, uid, [],
                            pricelist=sale_order.pricelist_id.id,
                            product=product_id, qty=1,
                            partner_id=sale_order.partner_id.id,
                            lang=sale_order.partner_id.lang, update_tax=True,
                            date_order=sale_order.date_order,
                            context=context)
                        value = res.get('value')
                        if value:
                            value['invoice_id'] = invoice.id
                            value['product_id'] = product_id
                            value['price_unit'] = sale_line.emergency_costs
                            value['quantity'] = 1
                            value['invoice_line_tax_id'] = value.get('tax_id') and [(6, 0, value.get('tax_id'))] or [(6, 0, [])]
                        invoice_line_obj.create(cr, uid, value, context=context)
                        sale_line_obj.write(cr, uid, [sale_line.id], {'emergency_costs_generated' : True}, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: