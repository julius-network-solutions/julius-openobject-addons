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
    def _group_line_by_order(self, lines):
        res = {}
        for line in lines:
            for sale_line in line.sale_line_ids:
                if sale_line.order_id and \
                    sale_line.order_id.global_discount_percentage:
                    order_id = sale_line.order_id.id
                    res.setdefault(order_id, [])
                    res[order_id].append(line)
                    continue
        return res

    @api.one
    def generate_global_discount(self, discount_percentage=None, many=False):
        if not many:
            super(account_invoice, self).\
                generate_global_discount(discount_percentage)
        else:
            line_obj = self.env['account.invoice.line']
            order_obj = self.env['sale.order']
            lines = line_obj.search([('invoice_id', '=', self.id)])
            line_by_order = self._group_line_by_order(lines)
            if isinstance(line_by_order, list):
                line_by_order = line_by_order and line_by_order[0] or {}
            for order_id in line_by_order.keys():
                invoice_lines = line_by_order.get(order_id)
                line_by_taxes = self._get_lines_by_taxes(invoice_lines)
                order = order_obj.browse(order_id)
                discount = order.global_discount_percentage or 0
                if discount:
                    self._create_global_lines_discount_by_taxes(line_by_taxes,
                                                                discount)
            self.button_compute(self.id)

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    global_discount = fields.Boolean('Global Discount', readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
