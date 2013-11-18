# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _fill_in_edi_prodlot(cr, uid, move_id, context=None):
        """
        This will update serial numbers with the good company
        """
        if context is None:
            context = {}
        stock_prodlot_obj = self.pool.get('stock.production.lot')
        # For each moves we get the picking
        pick = self.browse(cr, uid,
                           move_id, context=context).picking_id
        if pick:
            for move_line in pick.move_lines:
                # For each moves in the picking
                # we update the company
                # if there is a prodlot defined
                if move_line.prodlot_id:
                    prodlot = move_line.prodlot_id
                    company_id = prodlot.current_location_id and \
                        prodlot.current_location_id.company_id and \
                        prodlot.current_location_id.company_id.id or False
                    if company_id != prodlot.company_id:
                        stock_prodlot_obj.write(cr, uid,
                                                prodlot.id, {
                                                'company_id': company_id,
                                                },context=context)
        return True

    def _fill_in_edi_prodlot(cr, uid, move_id, context=None):
        """
        This will fill in the serial numbers for the related
        edi picking when set this move to "done"
        """
        if context is None:
            context = {}
        stock_picking_obj = self.pool.get('stock.picking')
        # For each moves we get the picking
        pick = self.browse(cr, uid,
                           move_id, context=context).picking_id
        if pick:
            # We check if the picking is an edi
            # and if type is out and the picking get a edi_id
            if pick.is_edi and pick.edi_id and pick.type == 'out':
                # If the moves got production lots,
                # we get the list of production lots by products
                prodlots = {}
                for move_line in pick.move_lines:
                    if move_line.prodlot_id:
                        # If the product in the list we put it to empty list
                        # + append the production lot in the list
                        prodlots.setdefault(move_line.product_id.id, []).\
                            append(move_line.prodlot_id.id)
                pick_in = stock_picking_obj.browse(
                    cr, SUPERUSER_ID, pick.edi_id.id, context=context)
                
                # for the production lots found,
                # we get the list of moves by products
                move_line_in = {}
                for move_line in pick_in.move_lines:
                    if prodlots.get(move_line.product_id.id):
                        # If the product in the list we put it to empty list
                        # + append the move in the list
                        move_line_in.setdefault(move_line.product_id.id, []).\
                            append(move_line.id)
                
                # This make possible to update moves
                # with related production lots
                for product_id in prodlots.keys():
                    for move_id in move_line_in[product_id]:
                        prodlot_id = prodlots[product_id].pop()
                        self.write(cr, SUPERUSER_ID, move_id, {
                                   'prodlot_id' : prodlot_id,
                                   }, context=context)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        """
        Inherit the write method for the stock move
        """
        if context is None:
            context = {}
        # If the ids value is not a list,
        # this change the type to list to be able to loop it !
        if not isinstance(ids, list): ids = [ids]
        # Run the native move write method
        res = super(stock_move, self).\
            write(cr, uid, ids, vals, context=context)
        # If we get 'state' in the vals and the value is "done":
        if vals.get('state') == 'done':
            for move_id in ids:
                # Update the company for production lots
                self._update_prodlot_company(cr, uid, move_id, context=context)
                # Fill move with the production lots
                self._fill_in_edi_prodlot(cr, uid, move_id, context=context)
        return res

    def _update_vals_with_location_and_dest(self, cr, uid,
                                            vals=None, context=None):
        """
        This method will return the vals updated
        with the location and destination related
        to the sale order or purchase order
        """
        if context is None:
            context = {}
        if vals is None:
            vals = {}
        sale_line_id = vals.get('sale_line_id')
        purchase_line_id = vals.get('purchase_line_id')
        company_id = vals.get('company_id')
        if company_id and (sale_line_id or purchase_line_id):
            sale_line_obj = self.pool.get('sale.order.line')
            purchase_line_obj = self.pool.get('purchase.order.line')
            stock_warehouse_obj = self.pool.get('stock.warehouse')
            data_obj = self.pool.get('ir.model.data')
            model, location_multi_id = data_obj.get_object_reference(
                cr, uid, 'multicompany_warehouse', 'multicompany_location')
            warehouse_ids = stock_warehouse_obj.search(
                cr, uid, [
                    ('company_id','=',company_id),
                ], limit=1, context=context)
            warehouse_id = warehouse_ids and warehouse_ids[0] or False
            if warehouse_id:
                warehouse = stock_warehouse_obj.browse(
                    cr, SUPERUSER_ID, warehouse_id, context=context)
                if sale_line_id:
                    sale = sale_line_obj.browse(
                        cr, uid, sale_line_id, context=context).order_id
                    if sale:
                        if sale.purchase_order_id:
                            vals.update({
                                'location_id': warehouse.lot_stock_id.id,
                                'location_dest_id': location_multi_id,
                            })
                elif purchase_line_id:
                    purchase = purchase_line_obj.browse(
                        cr, uid, purchase_line_id, context=context).order_id
                    if purchase:
                        if purchase.sale_order_id:
                            vals.update({
                                'location_id': location_multi_id,
                                'location_dest_id': warehouse.lot_stock_id.id,
                            })
        return vals
        

    def create(self, cr, uid, vals, context=None):
        """
        Inherit the create method for the stock move
        """
        if context is None:
            context = {}
        vals = self._update_vals_with_location_and_dest(
            cr, uid, vals, context=context)
        return super(stock_move, self).create(cr, uid, vals, context=context)
    
class stock_picking(orm.Model):
    _inherit = "stock.picking"
    
    def _get_is_edi(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        sale_obj = self.pool.get('sale.order')
        purchase_obj = self.pool.get('purchase.order')
        for stock_picking in self.browse(cr, uid, ids, context=context):
            res[stock_picking.id] = False
            if stock_picking.sale_id:
                sale = sale_obj.browse(cr, uid, stock_picking.sale_id.id, context=context)
                if sale.purchase_order_id:
                    res[stock_picking.id] = True
            if stock_picking.purchase_id:
                purchase = purchase_obj.browse(cr, 1, stock_picking.purchase_id.id, context=context)
                if purchase.sale_order_id:
                    res[stock_picking.id] = True
        return res
    
    _columns = {
        'is_edi' : fields.function(_get_is_edi, string='Is EDI', type='boolean', store=True),
        'edi_id' : fields.many2one('stock.picking','EDI id')
    }
    
    def edi_link(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        purchase_obj = self.pool.get('purchase.order')
        for stock_picking in self.browse(cr, uid, ids, context=context):
            if stock_picking.sale_id:
                sale = sale_obj.browse(cr, uid, stock_picking.sale_id.id, context=context)
                if sale.purchase_order_id:
                    link_picking_ids = self.search(cr, SUPERUSER_ID, [('purchase_id','=', sale.purchase_order_id.id)], context=context)
                    if link_picking_ids:
                        self.write(cr, SUPERUSER_ID, link_picking_ids[0], {'edi_id': stock_picking.id}, context=context)
                        self.write(cr, SUPERUSER_ID, stock_picking.id, {'edi_id': link_picking_ids[0]}, context=context)
            if stock_picking.purchase_id:
                purchase = purchase_obj.browse(cr, SUPERUSER_ID, stock_picking.purchase_id.id, context=context)
                if purchase.sale_order_id:
                    link_picking_ids = self.search(cr, SUPERUSER_ID, [('sale_id','=', purchase.sale_order_id.id)], context=context)
                    if link_picking_ids:
                        self.write(cr, SUPERUSER_ID, link_picking_ids[0], {'edi_id': stock_picking.id}, context=context)
                        self.write(cr, SUPERUSER_ID, stock_picking.id, {'edi_id': link_picking_ids[0]}, context=context)
        return True
        
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        purchase_obj = self.pool.get('purchase.order')
        user_obj = self.pool.get('res.user')
        stock_warehouse_obj = self.pool.get('stock.warehouse')
        data_obj = self.pool.get('ir.model.data')
        sale_id = vals.get('sale_id')
        purchase_id = vals.get('purchase_id') 
        model, location_multi_id = data_obj.get_object_reference(cr, uid, 'multicompany_warehouse', 'multicompany_location')
        company_id = vals.get('company_id')
        if company_id:
            warehouse_id = stock_warehouse_obj.search(cr, uid, [('company_id','=',company_id)], context=context)
            warehouse = stock_warehouse_obj.browse(cr, SUPERUSER_ID, warehouse_id[0],context=context)
            if sale_id:
                sale = sale_obj.browse(cr, uid, sale_id, context=context)
                if sale.purchase_order_id:
                    vals['location_id'] = warehouse.lot_stock_id.id
                    vals['location_dest_id'] = location_multi_id
            if purchase_id:
                purchase = purchase_obj.browse(cr, uid, purchase_id, context=context)
                if purchase.sale_order_id:
                    vals['location_id'] = location_multi_id
                    vals['location_dest_id'] = warehouse.lot_stock_id.id
        res = super(stock_picking, self).create(cr, uid, vals, context=context)
        self.edi_link(cr, uid, [res], context)
        return res
    
class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'
    
    def _get_is_edi(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        sale_obj = self.pool.get('sale.order')
        purchase_obj = self.pool.get('purchase.order')
        for stock_picking in self.browse(cr, uid, ids, context=context):
            res[stock_picking.id] = False
            if stock_picking.sale_id:
                sale = sale_obj.browse(cr, uid, stock_picking.sale_id.id, context=context)
                if sale.purchase_order_id:
                    res[stock_picking.id] = True
        return res
    
    _columns = {
        'is_edi' : fields.function(_get_is_edi, string='Is EDI', type='boolean', store=True),
        'edi_id' : fields.many2one('stock.picking','EDI id')
    }
    
    def edi_link(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        purchase_obj = self.pool.get('purchase.order')
        for stock_picking in self.browse(cr, uid, ids, context=context):
            if stock_picking.sale_id:
                sale = sale_obj.browse(cr, uid, stock_picking.sale_id.id, context=context)
                if sale.purchase_order_id:
                    link_picking_ids = self.search(cr, SUPERUSER_ID, [('purchase_id','=', sale.purchase_order_id.id)], context=context)
                    if link_picking_ids:
                        self.write(cr, SUPERUSER_ID, link_picking_ids[0], {'edi_id': stock_picking.id}, context=context)
                        self.write(cr, SUPERUSER_ID, stock_picking.id, {'edi_id': link_picking_ids[0]}, context=context)
        return True
    
    
class stock_picking_in(orm.Model):
    _inherit = 'stock.picking.in'
    
    def _get_is_edi(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        sale_obj = self.pool.get('sale.order')
        purchase_obj = self.pool.get('purchase.order')
        for stock_picking in self.browse(cr, uid, ids, context=context):
            res[stock_picking.id] = False
            if stock_picking.purchase_id:
                purchase = purchase_obj.browse(cr, uid, stock_picking.purchase_id.id, context=context)
                if purchase.sale_order_id:
                    res[stock_picking.id] = True
        return res
    
    _columns = {
        'is_edi' : fields.function(_get_is_edi, string='Is EDI', type='boolean', store=True),
        'edi_id' : fields.many2one('stock.picking','EDI id')
    }

    def edi_link(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        purchase_obj = self.pool.get('purchase.order')
        for stock_picking in self.browse(cr, uid, ids, context=context):
            if stock_picking.purchase_id:
                purchase = purchase_obj.browse(cr, SUPERUSER_ID, stock_picking.purchase_id.id, context=context)
                if purchase.sale_order_id:
                    link_picking_ids = self.search(cr, SUPERUSER_ID, [('sale_id','=', purchase.sale_order_id.id)], context=context)
                    if link_picking_ids:
                        self.write(cr, SUPERUSER_ID, link_picking_ids[0], {'edi_id': stock_picking.id}, context=context)
                        self.write(cr, SUPERUSER_ID, stock_picking.id, {'edi_id': link_picking_ids[0]}, context=context)
        return True
    
    def action_process(self, cr, uid, ids, context=None):
        picking = self.browse(cr, uid, ids, context=context)
        if picking[0].is_edi:
            if picking[0].edi_id:
                picking_out = self.browse(cr, 1, picking[0].edi_id.id, context=context)
                if picking_out.state == 'done':
                    res = super(stock_picking_in,self).action_process(cr, uid, ids, context=context)
                    return res
            raise orm.except_orm(_('Error'), _('The Delivery Order (%s) linked with this Incomming Shipment is not Done yet') % (picking_out.name))
        else:
            res = super(stock_picking_in,self).action_process(cr, uid, ids, context=context)
        return res
