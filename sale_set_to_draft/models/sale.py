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

from openerp import models, api, workflow


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_cancel_draft(self):
        lines = self.env['sale.order.line'].\
            search([
                    ('order_id', 'in', self.ids),
                    ('state', '=', 'cancel'),
                    ])
        self.write({
                    'state': 'draft',
                    'invoice_ids': [(6, 0, [])],
                    'shipped': 0,
                    })
        lines.write({
                     'invoiced': False,
                     'state': 'draft',
                     'invoice_lines': [(6, 0, [])],
                     })
        for sale in self:
            # Deleting the existing instance of workflow for SO
            workflow.trg_delete(self._uid, 'sale.order', sale.id, self._cr)
            workflow.trg_create(self._uid, 'sale.order', sale.id, self._cr)
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
