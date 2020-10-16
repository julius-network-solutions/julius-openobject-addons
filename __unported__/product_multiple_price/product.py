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
import openerp.addons.decimal_precision as dp

class product_product(orm.Model):
    _inherit = "product.product"
    
    def _compute_multiple_price(self, cr, uid, ids, names, arg, context=None):
        ## Init ##
        res = {}
        if context is None:
            context = {}
        if not isinstance(names, list):
            names = [names]
        for product in self.browse(cr, uid, ids, context=context):
            data = {}
            for name in names:
                ## Multiplication factor determination ##
                factor = 0
                if name == 'price_1000_unit':
                    factor = 1000
                elif name == 'price_100_unit':
                    factor = 100
                elif name == 'price_10_unit':
                    factor = 10
                elif name == 'price_1_unit':
                    factor = 1
                ## Process ##
                data[name] = 0
                if product.price_type == '1000_unit':
                    data[name] =  product.price_data * factor / 1000
                elif product.price_type == '100_unit':
                    data[name] =  product.price_data * factor / 100
                elif product.price_type == '10_unit':
                    data[name] = product.price_data * factor / 10
                elif product.price_type == '1_unit':
                    data[name] = product.price_data * factor
            res[product.id] = data
        return res
    
    _columns = {
        'price_data': fields.float('Price Data',
            digits_compute=dp.get_precision('Product Multi Price')),
        'price_type': fields.selection([
            ('1_unit', '1 Unit'),
            ('10_unit', '10 Units'),
            ('100_unit', '100 Units'),
            ('1000_unit', '1000 Units')
            ],'Price Type'),
        'price_1_unit': fields.function(
            _compute_multiple_price, type='float', string='Price 1 Unit',
            digits_compute=dp.get_precision('Product Multi Price'),
            multi="price", store=True),
        'price_10_unit': fields.function(
            _compute_multiple_price, type='float', string='Price 10 Units',
            digits_compute=dp.get_precision('Product Multi Price'),
            multi="price", store=True),
        'price_100_unit': fields.function(
            _compute_multiple_price, type='float', string='Price 100 Units', 
            digits_compute=dp.get_precision('Product Multi Price'),
            multi="price", store=True),
        'price_1000_unit': fields.function(
            _compute_multiple_price, type='float', string='Price 1000 Units', 
            digits_compute=dp.get_precision('Product Multi Price'),
            multi="price", store=True),
    }
    
    _defaults = {
        'price_type': '1_unit',
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
