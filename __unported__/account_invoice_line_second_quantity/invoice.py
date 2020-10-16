# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    
    second_quantity = fields.\
        Float('Second Quantity',
              digits= dp.get_precision('Product Unit of Measure'))
    second_uom_id = fields.Many2one('product.uom', 'Second UoM')

    @api.onchange('second_uom_id')
    def on_change_second_uom_id(self):
        uom_obj = self.env['product.uom']
        if self.uos_id and self.second_uom_id and not self.second_quantity:
            self.second_quantity = uom_obj.\
                _compute_qty(self.uos_id.id, self.quantity,
                             self.second_uom_id.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
