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

class product_average_price(orm.Model):
    _name = "product.average.price"
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'year': fields.integer('Year', required=True),
        'amount_init': fields.float('Initial Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_01': fields.float('January Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_02': fields.float('February Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_03': fields.float('March Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_04': fields.float('April Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_05': fields.float('May Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_06': fields.float('June Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_07': fields.float('July Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_08': fields.float('August Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_09': fields.float('September Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_10': fields.float('October Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_11': fields.float('November Amount', digits_compute=dp.get_precision('Product Price')),
        'amount_12': fields.float('December Amount', digits_compute=dp.get_precision('Product Price')),
        'stock_init': fields.float('Initial Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_01': fields.float('January Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_02': fields.float('February Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_03': fields.float('March Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_04': fields.float('April Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_05': fields.float('May Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_06': fields.float('June Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_07': fields.float('July Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_08': fields.float('August Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_09': fields.float('September Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_10': fields.float('October Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_11': fields.float('November Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
        'stock_12': fields.float('December Stock', digits_compute=dp.get_precision('Product Unit of Measure')),
    }
    
    _defaults = {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
