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

class res_partner(models.Model):
    """ Inherits res partner to add some needed fields """
    _inherit = 'res.partner'

    purchase_order_count2 = fields.Integer('# of Purchase Order',
                                           compute='_purchase_invoice_count2')
    supplier_invoice_count2 = fields.\
        Integer('# Supplier Invoices', compute='_purchase_invoice_count2')

    @api.one
    def _purchase_invoice_count2(self):
        """
        Get the number of purchases and invoices related to this partner
        """
        # The current user may not have access rights for purchases
        try:
            PurchaseOrder = self.env['purchase.order']
            self.purchase_order_count2 = PurchaseOrder.\
                search_count([('partner_id', '=', self.id)])
        except:
            self.purchase_order_count2 = 0
        # The current user may not have access rights for invoices
        try:
            Invoice = self.pool['account.invoice']
            self.supplier_invoice_count2 = Invoice.\
                search_count([
                              ('partner_id', '=', partner_id),
                              ('type','=','in_invoice')
                              ])
        except:
            self.supplier_invoice_count2 = 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
