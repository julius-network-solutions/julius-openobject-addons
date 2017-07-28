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
from odoo import models, fields, api

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    is_emergency_cost_line = fields.Boolean("Emergency cost line",
                                            default=False)
    @api.one
    def _get_is_cost_line(self):
        """
        Compute method for the field is_cost_line
        """
        super(AccountInvoiceLine, self)._get_is_cost_line()
        if self.is_emergency_cost_line:
            self.is_cost_line = True

    @api.model
    def create(self, vals):
        # Call super method
        invoice_line = super(AccountInvoiceLine, self).create(vals)
        
        # Create new invoice line for emergency costs if necessary
        product = self.env.ref('emergency_costs.product_emergency_costs')
        if not invoice_line.is_cost_line:
            for sale_line in invoice_line.sale_line_ids:
                if sale_line._emergency_line_to_create():
                    price_unit = sale_line.emergency_costs or 0
                    
                    # Create order line linked to order with emergency costs product
                    sale_order_line_env = self.env['sale.order.line']
                    vals = {'product_id': product.id,
                            'name': product.name,
                            'order_id': sale_line.order_id.id,
                            'product_uom': product.uom_id.id}
                    emergency_costs_sale_order_line = sale_order_line_env.new(vals)
                    emergency_costs_sale_order_line.product_id_change()

                    # Prepare invoice from sale order line created
                    vals = emergency_costs_sale_order_line._prepare_invoice_line(1)
                    
                    if vals:
                        tax_ids = sale_line.tax_id and \
                            [(6, 0, [x.id for x in sale_line.tax_id] or [])]
                        vals.update({'product_id': product.id,
                                     'price_unit': price_unit,
                                     'invoice_line_tax_ids': tax_ids,
                                     'invoice_id': invoice_line.invoice_id.id,
                                     'is_emergency_cost_line': True,
                                    })
                        new_invoice_line = self.env['account.invoice.line'].create(vals)

                        if new_invoice_line:
                            field = 'emergency_costs_line_id'
                            sale_line.write({'emergency_costs_line_id': new_invoice_line.id})


        return invoice_line


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
