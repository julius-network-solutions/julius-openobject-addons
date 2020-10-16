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

class product_consummation(orm.Model):
    _name = "product.consummation"
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'year': fields.integer('Year', required=True),
        'consummation_01': fields.float('January Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_02': fields.float('February Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_03': fields.float('March Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_04': fields.float('April Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_05': fields.float('May Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_06': fields.float('June Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_07': fields.float('July Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_08': fields.float('August Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_09': fields.float('September Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_10': fields.float('October Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_11': fields.float('November Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
        'consummation_12': fields.float('December Consummation', digits_compute=dp.get_precision('Product Unit of Measure')),
    }
    
    _defaults = {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
