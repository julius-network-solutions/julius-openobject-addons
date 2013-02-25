# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions (<http://www.julius.fr/>) contact@julius.fr
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


from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class stock_picking_fill_type(orm.Model):
    _name = 'stock.picking.fill.type'
    
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char('Name', size=64),
    }

class stock_picking_fill_product(orm.TransientModel):
    _name = 'stock.picking.fill.product'
    
    _columns = {
        'name': fields.char('Name', size=64),
        'fill_id': fields.many2one('stock.picking.fill', 'Fill ID'),
        'product_id': fields.many2one('product.product', 'Product',
                        domain="[('type', '!=', 'service'),('track_outgoing', '=', False)]", required=True),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'qty': fields.integer('Quantity'),
    }
    
    _defaults = {
        'picking_id': lambda self, cr, uid, context: context.get('default_picking_id') or False,
    }  
    
    def onchange_product_id(self, cr, uid, ids, product_id, picking_id, context=None):
        if context is None:
            context = {}
        res = {'value': {'qty': 0}}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        if product_id and picking_id:
            context['location'] = picking_obj.browse(cr, uid, picking_id, context=context).location_id.id
            context['states'] = ('done',)
            context['what'] = ('in', 'out')
            context['compute_child'] = True
            data = product_obj.get_product_available(cr, uid, [product_id], context=context)
            res['value']['qty'] = data[product_id]
        return res

class stock_picking_fill(orm.TransientModel):
    
    _name = 'stock.picking.fill'
    
    _columns = {
        'picking_id': fields.many2one('stock.picking', 'Picking', required=True),
        'type_id': fields.many2one('stock.picking.fill.type', 'Type', required=True),
        'type': fields.char('Type', size=64),
        'product_table_ids': fields.one2many('stock.picking.fill.product','fill_id','Products'),
#        'product_ids': fields.many2many('product.product', 'product_fill_picking_rel', 'wizard_id', 'product_id', 'Products', domain="[('type', '!=', 'service'),('track_outgoing', '=', False)]"),
    }
    
    def _get_type_id(self, cr, uid, context=None):
        if context == None:
            context = {}
        type = 'product'
        if context.get('type_selection'):
            type = context.get('type_selection')
        type_obj = self.pool.get('stock.picking.fill.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        return default_type and default_type[0] or False

    def _get_type(self, cr, uid, context=None):
        if context == None:
            context = {}
        type = 'product'
        if context.get('type_selection'):
            type = context.get('type_selection')
        res_type = ''
        type_obj = self.pool.get('stock.picking.fill.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        if default_type and default_type[0]:
            read_type = type_obj.read(cr, uid, default_type[0], ['code'], context=context)
            if read_type['code']:
                res_type = read_type['code']
        return res_type or ''
    
    _defaults = {
        'picking_id': lambda self, cr, uid, context: context.get('active_id') or False,
        'type_id': lambda self, cr, uid, context: self._get_type_id(cr, uid, context),
        'type': lambda self, cr, uid, context: self._get_type(cr, uid, context),
    }
    
    def onchange_type_id(self, cr, uid, ids, type_id):
        res = {'value': {'type': ''}}
        if type_id:
            type_obj = self.pool.get('stock.picking.fill.type')
            type = type_obj.read(cr, uid, type_id, ['code'])
            if type['code']:
                res = {'value': {'type': type['code']}}
        return res
    
    def _get_vals_product(self, cr, uid, current, picking_id, location_id, location_dest_id, context=None):
        res = []
        move_obj = self.pool.get('stock.move')
        if not current.product_table_ids:
            raise osv.except_osv(_('Invalid action !'),
                    _('There are no product to add please select at least 1 product to add to the picking !'))
        for line in current.product_table_ids:
            line.product_id.id
            result_vals = move_obj.onchange_product_id(cr, uid, [], prod_id=line.product_id.id,
                                loc_id=location_id, loc_dest_id=location_dest_id)
            line_vals = result_vals and result_vals.get('value') or False
            if line_vals:
                line_vals.update({
                    'picking_id': picking_id,
                    'product_id': line.product_id.id,
                    'product_qty': line.qty
                })
                res.append(line_vals)
        return res
    
    def _get_vals(self, cr, uid, current, context=None):
        res = []
        picking = current.picking_id or False
        if not picking:
            return []
        else:
            picking_id = picking.id
            location_id = picking.location_id and picking.location_id.id or False
            location_dest_id = picking.location_dest_id and picking.location_dest_id.id or False
            if not location_id or not location_dest_id:
                return []
        if current.type_id.code == 'product':
            res = self._get_vals_product(cr, uid, current, picking_id=picking_id, location_id=location_id,
                    location_dest_id=location_dest_id,  context=context)
        return res
    
    def fill_picking(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        current = self.browse(cr, uid, ids[0], context=context)
        lines = self._get_vals(cr, uid, current, context=context)
        for line in lines:
            self.pool.get('stock.move').create(cr, uid, line, context=context)
        return {'type': 'ir.actions.act_window_close'}                

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
