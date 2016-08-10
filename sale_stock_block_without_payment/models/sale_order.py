# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    Copyright (C) 2015: Ursa Information Systems
#    Author: Sandip Mangukiya (<smangukiya@ursainfosystems.com>)
#    Website:(<http://www.ursainfosystems.com>).
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


from datetime import datetime
from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_order_blocked(self):
        blocked = False
        for inv in self.invoice_ids:
            today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
            if inv.date_due <= today and inv.state != 'paid' and \
                (self.payment_term_id and
                 self.payment_term_id.block_without_payment) and not \
               self.marked_as_paid:
                blocked = True
            if inv.state == 'paid':
                blocked = False
        if not self.invoice_ids and self.payment_term_id and \
                self.payment_term_id.block_without_payment:
            blocked = True
        self.block_without_payment = blocked

    marked_as_paid = fields.Boolean('Marked as Paid', readonly=True,
                                    default=False)

    block_without_payment = fields.Boolean(compute=_get_order_blocked,
                                           string='Block Order Without '
                                                  'Payment')

    def set_marked_as_paid(self):
        return self.write({'marked_as_paid': True})

    def set_marked_as_unpaid(self):
        return self.write({'marked_as_paid': False})
