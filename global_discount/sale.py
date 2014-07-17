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

# from openerp.tools.translate import _
from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning

class sale_order(models.Model):
    _inherit = 'sale.order'

    global_discount_percentage = fields.\
        Float('Discount Percentage',
              readonly=True, states={
                                     'draft':[('readonly',False)],
                                     'sent':[('readonly',False)],
                                     })
    global_discount_display = fields.\
        Char('Discount', size=32,
             compute='_discount_display')
    amount_untaxed_discounted = fields.\
        Float('Untaxed Amount With Discount',
              digits_compute=dp.get_precision('Account'),
              compute='_amount_discounted',
              store=True)
    amount_tax_discounted = fields.\
        Float('Taxes With Discount',
              digits_compute=dp.get_precision('Account'),
              compute='_amount_discounted',
              store=True)
    amount_total_discounted = fields.\
        Float('Total With Discount',
              digits_compute=dp.get_precision('Account'),
              compute='_amount_discounted',
              store=True)
    discount_is_present = fields.\
        Boolean('Discount Present',
                compute='_check_if_discount')
    amount_total_display = fields.\
        Float('Total',
              digits_compute=dp.get_precision('Account'),
              compute='_amount_discounted',
              store=True)

    @api.one
    @api.depends('amount_untaxed','amount_tax','global_discount_percentage',
                 'order_line','order_line.product_uom_qty',
                 'order_line.price_unit','order_line.tax_id')
    def _amount_discounted(self):
        """
        Function computing the taxes total
        with discount of sale orders.
        """
        discount = (100 - self.global_discount_percentage) / 100
        self.amount_untaxed_discounted = self.amount_untaxed * discount
        self.amount_tax_discounted = self.amount_tax * discount
        self.amount_total_discounted = self.amount_untaxed_discounted + \
            self.amount_tax_discounted
        self.amount_total_display = self.global_discount_percentage and \
            self.amount_total_discounted or self.amount_total

    @api.one
    @api.depends('global_discount_percentage')
    def _discount_display(self):
        self.global_discount_display = '- %.2f %%' %self.global_discount_percentage
        
    @api.one
    @api.depends('order_line','global_discount_percentage')
    def _check_if_discount(self):
        """
        Function checking if there is
        a discount in the sale order.
        """
        self.discount_is_present = False
        if self.global_discount_percentage:
            self.discount_is_present = True
        else:
            for line in self.order_line:
                if line.global_discount == True:
                    self.discount_is_present = True
                    break

    @api.one
    def _get_lines_by_taxes(self, lines=None):
        """ This method will return a dictionary of taxes as keys
        with the related lines.
        """
        if lines is None:
            lines = self.order_line
        res = {}
        for line in lines:
            taxes = [x.id for x in line.tax_id]
            if taxes:
                taxes.sort()
            taxes_str = str(taxes)
            res.setdefault(taxes_str, [])
            res[taxes_str].append(line)
        return res

    @api.one
    def _create_global_lines_discount_by_taxes(self, line_by_taxes):
        discount = self.global_discount_percentage / 100
        product = self.env.ref('global_discount.product_global_discount')
        line_obj = self.env['sale.order.line']
        if isinstance(line_by_taxes, list):
            line_by_taxes = line_by_taxes and line_by_taxes[0] or {}
        for tax_str in line_by_taxes.keys():
            line_sum = 0
            discount_value = 0
            order = False
            line = False
            for line in line_by_taxes[tax_str]:
                qty = line.product_uom_qty
                pu = line.price_unit
                sub = qty * pu
                line_sum += sub
                discount_value = line_sum * discount
            if line:
                res_value = line_obj.\
                    product_id_change(pricelist=self.pricelist_id.id,
                                      product=product.id, qty=1,
                                      partner_id=self.partner_id.id,
                                      lang=self.partner_id.lang,
                                      update_tax=False,
                                      date_order=self.date_order,
                                      fiscal_position=self.fiscal_position)
                value = res_value.get('value')
                if value:
                    tax_ids = eval(tax_str)
                    tax_ids = [(6, 0, tax_ids)]
                    value.update({
                        'global_discount': True,
                        'price_unit': -discount_value,
                        'order_id': self.id,
                        'product_id': product.id,
                        'product_uos_qty': 1,
                        'tax_id': tax_ids, 
                    })
                    new_line = line_obj.create(value)
                    new_line.product_uom_qty = 1

    @api.one
    def generate_global_discount(self):
        if self.state in ('draft','sent') and \
            self.global_discount_percentage != 0.00:
            domain = [
                ('order_id', '=', self.id),
                ('global_discount', '=', True),
                ('state', '=', 'draft'),
                ]
            line_obj = self.env['sale.order.line']
            lines = line_obj.search(domain)
            if lines:
                lines.unlink()
            line_by_taxes = self._get_lines_by_taxes()
            self._create_global_lines_discount_by_taxes(line_by_taxes)
            self.global_discount_percentage = 0

    def _make_invoice(self, cr, uid, order, lines, context=None):
        if context is None:
            context = {}
        inv_id = super(sale_order, self).\
            _make_invoice(cr, uid, order, lines, context=None)
        if order.global_discount_percentage:
            invoice_obj = self.pool.get('account.invoice')
            invoice_obj.\
                generate_global_discount(cr, uid, [inv_id],
                                         order.global_discount_percentage,
                                         context=context)
        return inv_id

    @api.one
    @api.constrains('global_discount_percentage')
    def _check_global_discount_percentage(self):
        if self.global_discount_percentage and \
            (self.global_discount_percentage < 0 or \
            self.global_discount_percentage > 100):
            raise Warning(_('Discount value should be between 0 and 100'))

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    global_discount = fields.Boolean('Global Discount', readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
