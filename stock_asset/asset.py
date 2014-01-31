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

from osv import orm, fields
from tools.translate import _

class product_product(orm.Model):
    _inherit = 'product.product'
    
    _columns = {
        'financial_asset': fields.boolean('Is a financial Asset'),
    }

class stock_move(orm.Model):
    _inherit = 'stock.move'
    
    _columns = {
        'generate_asset': fields.boolean('Generate Asset'),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        user_obj = self.pool.get('res.users')
        model_data = self.pool.get('ir.model.data')
        asset_obj = self.pool.get('account.asset.asset')
        asset_categ_obj = self.pool.get('account.asset.category')
        result = super(stock_move, self).write(cr, uid, ids, vals, context=context)
        if not isinstance(ids, list):
            ids = [ids]
        # Loop #
        for move in self.browse(cr, uid, ids, context=context): 
            asset_ids = []
            asset_ids = asset_obj.search(cr, uid, [('prodlot_id','=',move.prodlot_id.id)], limit=1)
            if (move.state == 'done' and asset_ids == [] and (move.generate_asset == True or move.product_id.financial_asset == True)):
                # Initialization #
                date = move.date
                partner_id = False
                purchase_value = 0
                if move.purchase_line_id:
                    purchase_value = move.purchase_line_id.price_unit
                    date = move.purchase_line_id.date_planned
                else:
                    purchase_value = move.product_id.standard_price
                # Move of date asset on rely
                if move.picking_id and move.picking_id.purchase_id and move.picking_id.purchase_id.partner_id:
                    partner_id = move.picking_id.purchase_id.partner_id.id
                elif move.picking_id and move.picking_id.partner_id:
                    partner_id = move.picking_id.partner_id.id
                user = user_obj.read(cr, uid, uid, ['company_id'], context=context)
                compagny_id = user.get('company_id', False)[0]
                category_ids = asset_categ_obj.search(cr, uid, [('company_id','=',compagny_id)], limit=1)
                if category_ids:
                    category_id = category_ids[0]
                else:
                    category_id = model_data.get_object_reference(cr, uid, 'stock_asset', 'account_asset_category_misc_operational')[1]
                # Process #
                create_vals = {
                    'name': move.product_id.name,
                    'category_id': category_id or False,
                    'code': move.prodlot_id.name or False,
                    'purchase_value': purchase_value,
                    'purchase_date': date,
                    'partner_id': partner_id,
                    'product_id': move.product_id and move.product_id.id or False,
                    'prodlot_id': move.prodlot_id and move.prodlot_id.id or False,
                    'move_id': move.id,
                    'picking_id':move.picking_id and move.picking_id.id or False,
                    'state': 'draft',
                }
                qty = move.product_qty
                while qty > 0:
                    qty -= 1
                    asset_obj.create(cr, uid, create_vals, context=context)
        return result
    
class account_asset_asset(orm.Model):
    _inherit = 'account.asset.asset'

    _columns = {
        'move_id': fields.many2one('stock.move', 'Move'),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot'),
        'product_id': fields.many2one('product.product', 'Product'),
    }
    
    _sql_constraints = [
        ('prodlot_unique', 'unique (prodlot_id,company_id)', 'This prodlot is already link to an asset !'),
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: