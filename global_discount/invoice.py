# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def _get_lines_by_taxes(self, cr, uid, invoice_id,
                            line_ids=False, context=None):
        """ This method will return a dictionary of taxes as keys
        with the related lines.
        """
        if context is None:
            context = {}
        res = {}
        invoice = self.browse(cr, uid, invoice_id, context=context)
        for line in invoice.invoice_line:
            if line_ids and line.id not in line_ids:
                continue
            taxes = [x.id for x in line.invoice_line_tax_id]
            if taxes:
                taxes.sort()
            taxes_str = str(taxes)
            res.setdefault(taxes_str, [])
            res[taxes_str].append(line)
        return res

    def _create_global_discount_lines_by_taxes(self, cr, uid, discount,
                                               line_by_taxes, product_id,
                                               context=None):
        if context is None:
            context = {}
        res = []
        line_obj = self.pool.get('account.invoice.line')
        for tax_str in line_by_taxes.keys():
            line_sum = 0
            line = False
            invoice = False
            for line in line_by_taxes[tax_str]:
                qty = line.quantity
                pu = line.price_unit
                sub = qty * pu
                line_sum += sub
                discount_value = line_sum * discount
            if line and discount_value > 0:
                invoice = line.invoice_id
                partner_id = invoice.partner_id and \
                    invoice.partner_id.id or False
                fposition_id = invoice.fiscal_position and \
                    invoice.fiscal_position.id or False
                currency_id = invoice.currency_id and \
                    invoice.currency_id.id or False
                company_id = invoice.company_id and \
                    invoice.company_id.id or False
                res_value = line_obj.\
                    product_id_change(cr, uid, [line.id],
                    product_id, False, qty=1, partner_id=partner_id,
                    fposition_id=fposition_id, price_unit=discount_value,
                    currency_id=currency_id, context=context,
                    company_id=company_id)
                value = res_value.get('value')
                if value:
                    tax_ids = eval(tax_str)
                    tax_ids = [(6, 0, tax_ids)]
                    value.update({
                        'global_discount': True,
                        'invoice_id': invoice.id,
                        'product_id': product_id,
                        'price_unit': -discount_value,
                        'quantity': 1,
                        'invoice_line_tax_id': tax_ids,
                    })
                    res.append(line_obj.\
                        create(cr, uid, value, context=context))
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
