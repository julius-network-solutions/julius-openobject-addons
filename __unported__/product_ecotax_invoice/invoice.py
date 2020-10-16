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
import openerp.addons.decimal_precision as dp

class account_invoice(orm.Model):
    _inherit = "account.invoice"
    
    _columns = {
        'sale_order_ids': fields.many2many('sale.order', 'sale_order_invoice_rel',
                                           'invoice_id', 'order_id', 'Sale Order',
                                           readonly=True),
    }
    
    def _check_if_ecotax(self, cr, uid, line, context=None):
        if context is None:
            context = {}
        if not line.product_id or \
            (not line.product_id.ecotax_type in ['1','2'] and \
             not line.product_id.categ_id.ecotax_type in ['1','2'])and \
             not line.invoice_id.partner_id.country_id.subject_to_ecotax is True:
            return False
        return True
    
    def generate_ecotax_line(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('account.invoice.line')
        for invoice in self.browse(cr, uid, ids, context=context):
            product_list = {}
            if invoice.state != 'draft':
                continue
            for line in invoice.invoice_line:
                if not self._check_if_ecotax(cr, uid, line, context=context):
                    continue
                if line.product_id.ecotax_product_id and \
                    line.product_id.ecotax_product_id.id not in product_list.keys():
                    product_list.update({line.product_id.ecotax_product_id.id: line.quantity})
                elif line.product_id.ecotax_product_id:
                    product_list[line.product_id.ecotax_product_id.id] += line.quantity
                elif line.product_id.categ_id.ecotax_product_id and \
                    line.product_id.categ_id.ecotax_product_id.id not in product_list.keys():
                    product_list.update({line.product_id.categ_id.ecotax_product_id.id: line.quantity})
                elif line.product_id.categ_id.ecotax_product_id:
                    product_list[line.product_id.categ_id.ecotax_product_id.id] += line.quantity
            line_obj._genrate_ecotax_lines(cr, uid, invoice, product_list, context=context)
        return True
    
    def _amount_ecotax(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_ecotax': 0.0,
            }
            val = 0.0
            cur = invoice.currency_id
            for line in invoice.invoice_line:
                if line.ecotax:
                    val += line.price_subtotal
            res[invoice.id]['amount_ecotax'] = cur_obj.round(cr, uid, cur, val)
        return res
    
    def _get_invoices(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(
                                        cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    _columns = {
        'amount_ecotax': fields.function(_amount_ecotax,
            digits_compute=dp.get_precision('Account'), 
            string='Included ecotax', store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),
                'account.invoice.line': (_get_invoices,
                     ['price_unit', 'invoice_line_tax_id', 'discount', 'quantity', 'ecotax'],
                     20),
            },
            multi='sums', help="The included ecotax amount."),
    }
    
class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    _columns = {
        'ecotax': fields.boolean('Ecotax line'),
    }

    _defaults = {
        'ecotax': False,
        'sequence': 1,
    }

    def _genrate_ecotax_lines(self, cr, uid, invoice,
                              product_list, context=None):
        if context is None:
            context = {}
        line_to_del_ids = self.search(cr, uid, [
                ('invoice_id', '=', invoice.id),
                ('ecotax', '=', True),
                ('invoice_id.state', '=', 'draft'),
            ], context=context)
        self.unlink(cr, uid, line_to_del_ids, context=context)
        for product_id in product_list.keys():
            res = self.product_id_change(cr, uid, [], product=product_id,
                uom_id=False, qty=product_list[product_id], name='',
                type='out_invoice', partner_id=invoice.partner_id.id,
                fposition_id=invoice.fiscal_position.id,
                price_unit=False, currency_id=invoice.currency_id.id,
                context=context)
            vals = res.get('value')
            if vals:
                invoice_line_tax_id = vals.get('invoice_line_tax_id', [])
                vals.update({
                    'ecotax': True,
                    'invoice_id': invoice.id,
                    'product_id': product_id,
                    'quantity': product_list[product_id],
                    'sequence': 1000,
                    'invoice_line_tax_id': [(6, 0, invoice_line_tax_id)]
                })
                self.create(cr, uid, vals, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
