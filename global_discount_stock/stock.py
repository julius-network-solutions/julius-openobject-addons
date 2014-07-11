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
from openerp import models, api, fields

class stock_picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_invoice_create(self, journal_id=False,
                              group=False, type='out_invoice'):
        res = super(stock_picking, self).\
            action_invoice_create(journal_id=journal_id,
                                  group=group, type=type)
        invoice_obj = self.env['account.invoice']
        for invoice in invoice_obj.browse(res):
            if len(self.ids) == 1:
                discount = self.sale_id and \
                    self.sale_id.global_discount_percentage or 0.0
                if discount:
                    invoice.generate_global_discount(discount)
            else:
                invoice.generate_global_discount(many=True)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
