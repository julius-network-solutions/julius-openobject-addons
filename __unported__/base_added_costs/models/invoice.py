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

from openerp import models, fields, api


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _get_added_cost_line_value(self, sale_line, product_id, price_unit):
        sale_line_obj = self.env['sale.order.line']
        sale_order = sale_line.order_id
        res = sale_line_obj.\
            product_id_change(pricelist=sale_order.pricelist_id.id,
                              product=product_id, qty=1,
                              partner_id=sale_order.partner_id.id,
                              lang=sale_order.partner_id.lang,
                              update_tax=False,
                              date_order=sale_order.date_order)
        value = res.get('value', {})
        if value:
            tax_id = sale_line.tax_id and \
                [(6, 0, [x.id for x in sale_line.tax_id] or [])]
            value.update({
                          'product_id': product_id,
                          'price_unit': price_unit,
                          'quantity': 1,
                          'invoice_line_tax_id': tax_id,
                          })
        return value


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    @api.returns('account.invoice.line')
    def _create_added_cost_line(self, value, sale_line):
        if isinstance(value, list):
            value = value and value[0] or {}
        return self.create(value)

    linked_invoice_line_id = fields.Many2one('account.invoice.line',
                                             'Linked invoice_line',
                                             default=False)

    is_cost_line = fields.Boolean(compute='_get_is_cost_line')

    @api.one
    def _get_is_cost_line(self):
        """
        Compute method for the field is_cost_line
        """
        self.is_cost_line = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
