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

from openerp.tools.translate import _
from openerp import models, api, fields

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def _get_lines_by_taxes(self, lines=None):
        """ This method will return a dictionary of taxes as keys
        with the related lines.
        """
        if lines is None:
            lines = self.invoice_lines
        res = {}
        for line in lines:
            taxes = [x.id for x in line.invoice_line_tax_id]
            if taxes:
                taxes.sort()
            taxes_str = str(taxes)
            res.setdefault(taxes_str, [])
            res[taxes_str].append(line)
        return res

    @api.one
    def _create_global_lines_discount_by_taxes(self, line_by_taxes,
                                               discount_percentage=None):
        discount = (discount_percentage or 0) / 100
        product = self.env.ref('global_discount.product_global_discount')
        line_obj = self.env['account.invoice.line']
        if isinstance(line_by_taxes, list):
            line_by_taxes = line_by_taxes and line_by_taxes[0] or {}
        for tax_str in line_by_taxes.keys():
            line_sum = 0
            line = False
            discount_value = 0
            for line in line_by_taxes[tax_str]:
                qty = line.quantity
                pu = line.price_unit
                sub = qty * pu
                line_sum += sub
                discount_value = line_sum * discount
            if line and discount_value > 0:
                invoice = self
                partner_id = invoice.partner_id and \
                    invoice.partner_id.id or False
                fposition_id = invoice.fiscal_position and \
                    invoice.fiscal_position.id or False
                currency_id = invoice.currency_id and \
                    invoice.currency_id.id or False
                company_id = invoice.company_id and \
                    invoice.company_id.id or False
                res_value = line_obj.\
                    product_id_change(product.id, False, qty=1,
                                      partner_id=partner_id,
                                      fposition_id=fposition_id,
                                      price_unit=discount_value,
                                      currency_id=currency_id,
                                      company_id=company_id)
                value = res_value.get('value')
                if value:
                    tax_ids = eval(tax_str)
                    tax_ids = [(6, 0, tax_ids)]
                    value.update({
                        'global_discount': True,
                        'invoice_id': invoice.id,
                        'product_id': product.id,
                        'price_unit': -discount_value,
                        'quantity': 1,
                        'invoice_line_tax_id': tax_ids,
                    })
                    new_line = line_obj.create(value)
                    new_line.quantity = 1

    @api.one
    def generate_global_discount(self, discount_percentage=None, many=False):
        line_obj = self.env['account.invoice.line']
        lines = line_obj.search([('invoice_id', '=', self.id), ('sale_line_ids', '!=', False)])
        line_by_taxes = self._get_lines_by_taxes(lines)
        self._create_global_lines_discount_by_taxes(line_by_taxes,
                                                    discount_percentage)
        self.button_compute(self.id)

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    global_discount = fields.Boolean('Global Discount', readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
