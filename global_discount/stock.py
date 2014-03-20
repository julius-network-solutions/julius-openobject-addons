# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
                              group=False, type='out_invoice', context=None):
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        data_obj = self.pool.get('ir.model.data')
        res = super(stock_picking, self).\
            action_invoice_create(cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None)

        model, product_id = data_obj.\
            get_object_reference(cr, uid,
                                 'global_discount',
                                 'product_global_discount')
        for picking in self.\
            browse(cr, uid, res.keys(), context=context):
            invoice_id = res[picking.id]
            if invoice_id:
                global_discount = picking.sale_id and \
                    picking.sale_id.global_discount_percentage or 0
                if global_discount:
                    discount = global_discount / 100
                    line_by_taxes = invoice_obj.\
                        _get_lines_by_taxes(cr, uid, invoice_id,
                                            context=context)
                    invoice_ids = invoice_obj.\
                        _create_global_discount_lines_by_taxes(cr, uid,
                                                               discount,
                                                               line_by_taxes,
                                                               product_id,
                                                               context=context)
                    invoice_obj.\
                        button_compute(cr, uid, [invoice_id], context=context)
        return res

class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    _columns = {
        'global_discount': fields.boolean('Global Discount'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
