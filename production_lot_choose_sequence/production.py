# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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

from osv import osv, fields
from tools.translate import _

class product_product(osv.osv):
    _inherit = 'product.product'
    
    _columns = {
        'lot_sequence_id': fields.many2one('ir.sequence', 'Production lot sequence'),
    }
    
product_product()

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    
    _defaults = {
        'name': lambda *a: '/',
    }
    
    def create(self, cr, uid, vals, context=None):
        if context==None:
            context = {}
        if vals.get('product_id'):
            if vals.get('name') and vals['name'] == '/' or not vals.get('name'):
                product = self.pool.get('product.product').browse(cr, uid, vals.get('product_id'), context=context)
                if product and product.lot_sequence_id:
                    vals['name'] = self.pool.get('ir.sequence').next_by_id(cr, uid, product.lot_sequence_id.id, context=context)
        return super(stock_production_lot, self).create(cr, uid, vals, context=context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if context==None:
            context = {}
        if default==None:
            default = {}
        lot = self.browse(cr, uid, id, context=context)
        if lot.product_id and lot.product_id.lot_sequence_id:
            default['name'] = self.pool.get('ir.sequence').next_by_id(cr, uid, lot.product_id.lot_sequence_id.id, context=context)
        return super(stock_production_lot, self).copy(cr, uid, id, default=default, context=context)
    
stock_production_lot()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: