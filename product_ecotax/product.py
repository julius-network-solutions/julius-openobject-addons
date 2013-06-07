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

class product_template(orm.Model):
    _inherit = "product.template"
    
    _columns = {
        'ecotax_type': fields.selection([
                 ('0','No Submitted'),
                 ('1', 'Submitted and Reportable'),
                 ('2', 'Submitted and Non-Reportable')
             ], 'Ecotax', required=True),
        'ecotax_product_id': fields.many2one('product.product', 'Ecotax linked product', domain=[('ecotax', '=', True)]),
        'ecotax': fields.boolean('Ecotax product?'),
    }
    
    _defaults = {
        'ecotax_type': '0',
        'ecotax': False,
    }

class product_category(orm.Model):
    _inherit = "product.category"
    
    _columns = {
        'ecotax_type': fields.selection([
                 ('0','No Submitted'),
                 ('1','Submitted and Reportable'),
                 ('2','Submitted and No Reportable')
             ], 'Ecotax', required=True),
        'ecotax_product_id': fields.many2one('product.product', 'Ecotax linked product', domain=[('ecotax', '=', True)]),
    }
    
    _defaults = {
        'ecotax_type': '0',
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
