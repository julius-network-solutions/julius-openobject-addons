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

class product_tag(orm.Model):
    _name = "product.partner.code"
    _description = "Partner product code"
    _rec_name = 'code'
    
    _columns = {
        'code': fields.char('Code', required=True, size=64),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
    }
    
class product_product(orm.Model):
    _inherit = 'product.product'
    
    _columns = {
        'partner_code_ids': fields.one2many('product.partner.code', 'product_id', 'Product partner codes'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
