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

from openerp.tools.translate import _
from openerp import models, api

class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    def generate_launch_costs_invoice_line(self):
        if self.state == 'draft':
            inv_line_obj = self.env['account.invoice.line']
            product = self.env.ref('launch_costs.product_launch_costs')
            product_id = product.id
            for invoice_line in self.invoice_line:
                for sale_line in invoice_line.sale_line_ids:
                    if sale_line._launch_line_to_create():
                        unit_price = sale_line.launch_costs or 0
                        value = self.\
                            _get_added_cost_line_value(sale_line, product_id,
                                                       unit_price)
                        value.update({'invoice_id': self.id})
                        new_inv_line = inv_line_obj.\
                            _create_added_cost_line(value, sale_line)
                        new_inv_line_id = new_inv_line and \
                            new_inv_line[0].id or False
                        if new_inv_line_id:
                            field = 'launch_costs_line_id'
                            sale_line.\
                                _update_sale_added_cost_line(new_inv_line_id,
                                                             field=field)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
