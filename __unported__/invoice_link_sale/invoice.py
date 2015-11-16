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

from openerp import models, fields
from openerp.tools.translate import _

class account_invoice(models.Model):
    _inherit = "account.invoice"

    sale_ids = fields.Many2many('sale.order', 'sale_order_invoice_rel',
                                'invoice_id', 'order_id', 'Sales',
                                readonly=True, copy=False)

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    sale_line_ids = fields.Many2many('sale.order.line',
                                     'sale_order_line_invoice_rel',
                                     'invoice_id', 'order_line_id',
                                     'Sale Lines', readonly=True, copy=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
