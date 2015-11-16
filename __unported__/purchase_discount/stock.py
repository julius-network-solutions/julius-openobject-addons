# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _prepare_invoice_line(self, cr, uid, group,
                              picking, move_line, invoice_id,
                              invoice_vals, context=None):
        res = super(stock_picking, self).\
            _prepare_invoice_line(cr, uid, group, picking=picking,
            move_line=move_line, invoice_id=invoice_id,
            invoice_vals=invoice_vals, context=None)
        if move_line.purchase_line_id:
            res['discount'] = move_line.purchase_line_id.discount or 0.00
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
