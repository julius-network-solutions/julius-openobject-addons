# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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

from odoo.addons.sale import models
from odoo import models, api, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    launch_costs = fields.Float('Launch Costs')
    launch_costs_line_id = fields.Many2one('account.invoice.line', 'Launch costs invoice line', copy=False)
    
    @api.multi
    def _launch_line_to_create(self):
        res = False
        if self.launch_costs != 0 \
                and not self.launch_costs_line_id or \
                self.launch_costs_line_id.invoice_id.state == 'cancel':
            res = True
        return res

    @api.depends('launch_costs')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        super(SaleOrderLine, self)._compute_amount()
        for line in self:
            price = (line.launch_costs or 0.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line['price_tax'] += taxes['total_included'] - taxes['total_excluded']
            line['price_total'] += taxes['total_included']
            line['price_subtotal'] += taxes['total_excluded']


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
