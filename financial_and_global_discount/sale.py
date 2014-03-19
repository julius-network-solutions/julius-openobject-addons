# -*- coding: utf-8 -*-
#################################################################################
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
#################################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _calc_amount_untaxed_all_discounted(self, cr, uid, ids,name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for sale_order in self.browse(cr, uid, ids, context=context):
            amount_untaxed = sale_order.amount_untaxed
            discount = (100 - sale_order.financial_discount_percentage - sale_order.global_discount_percentage) / 100
            amount_untaxed_all_discounted = amount_untaxed * discount
            res[sale_order.id] = amount_untaxed_all_discounted
        return res

    def _calc_amount_tax_all_discounted(self, cr, uid, ids,name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for sale_order in self.browse(cr, uid, ids, context=context):
            amount_tax = sale_order.amount_tax
            discount = (100 - sale_order.financial_discount_percentage - sale_order.global_discount_percentage) / 100
            amount_tax_all_discounted = amount_tax * discount
            res[sale_order.id] = amount_tax_all_discounted
        return res

    def _calc_amount_total_all_discounted(self, cr, uid, ids,name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for sale_order in self.browse(cr, uid, ids, context=context):
            amount_total_all_discounted = sale_order.amount_untaxed_all_discounted + sale_order.amount_tax_all_discounted
            res[sale_order.id] = amount_total_all_discounted
        return res

    def _check_if_all_discount(self, cr, uid, ids,name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for sale_order in self.browse(cr, uid, ids, context=context):
            res[sale_order.id] = False
            discount = False
            financial = False
            for line in sale_order.order_line:
                if line.global_discount == True:
                    discount = True
                if line.financial_discount ==True:
                    financial = True
            if discount == True and financial == True:
                res[sale_order.id] = True
        return res

    _columns = {
            'amount_untaxed_all_discounted' : fields.function(_calc_amount_untaxed_all_discounted,string='Untaxed Amount With All Discount', readonly=True),
            'amount_tax_all_discounted' : fields.function(_calc_amount_tax_all_discounted, string='Taxes With All Discount', readonly=True),
            'amount_total_all_discounted' : fields.function(_calc_amount_total_all_discounted, string='Total With All Discount', readonly=True),
            'all_discount_is_present' : fields.function(_check_if_all_discount, string='All Discount Present', readonly=True, type="boolean"),
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: