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

    def _update_prodlot_company(self, cr, uid, move_id, context=None):
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

    def _fill_in_edi_prodlot(self, cr, uid, move_id, context=None):
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
        # If the company is defined
        # and a sale order line or a purchase order line too
        if company_id and (sale_line_id or purchase_line_id):
            sale_line_obj = self.pool.get('sale.order.line')
            purchase_line_obj = self.pool.get('purchase.order.line')
            stock_warehouse_obj = self.pool.get('stock.warehouse')
            data_obj = self.pool.get('ir.model.data')
            # Get the id of the record location "multi-company"
            model, location_multi_id = data_obj.get_object_reference(
                cr, uid, 'intercompany_warehouse', 'intercompany_location')
            # Getting the default warehouse of the company
            # to be able to get the warehouse default stock
            warehouse_ids = stock_warehouse_obj.search(
                cr, uid, [
                    ('company_id', '=', company_id),
                ], limit=1, context=context)
            warehouse_id = warehouse_ids and warehouse_ids[0] or False
            if warehouse_id:
                warehouse = stock_warehouse_obj.browse(
                    cr, SUPERUSER_ID, warehouse_id, context=context)
                if sale_line_id:
                    # If we got a sale order line
                    # we update the location and destination
                    # like this:
                    # From: warehouse default stock
                    # To: multi company stock 
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
                    # If we got a purchase order line
                    # we update the location and destination
                    # like this:
                    # From: multi company stock
                    # To: warehouse default stock
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
        # Update the vals with the goods location an destination
        vals = self._update_vals_with_location_and_dest(
            cr, uid, vals, context=context)
        return super(stock_move, self).create(cr, uid, vals, context=context)

class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _get_is_edi(self, cr, uid, ids, name, args, context=None):
        """
        This method will return if the picking is or not an edi picking
        """
        if context is None:
            context = {}
        res = {}
        for stock_picking in self.browse(cr, uid, ids, context=context):
            res[stock_picking.id] = False
            # If this picking have a related purchase to the related sale
            # or a related sale to the related purchase,
            # This picking is an edi picking
            if (stock_picking.sale_id and \
                stock_picking.sale_id.purchase_order_id) or \
                (stock_picking.purchase_id and \
                stock_picking.purchase_id.sale_order_id):
                res[stock_picking.id] = True
        return res

    _columns = {
        # TODO: make it stored on modification of sale_id and purchase_id
        # or sale order "purchase_order_id" or purchase "sale_order_id"
        'is_edi': fields.function(_get_is_edi,
                                  string='Is EDI', type='boolean', store=True),
        'edi_id': fields.many2one('stock.picking', 'EDI id'),
    }

    def _edi_link(self, cr, uid, picking_id, context=None):
        """
        Method to update the related pickings
        """
        if context is None:
            context = {}
        domain = False
        picking = self.browse(cr, uid, picking_id, context=context)
        if self._name == 'stock.picking.out' and picking.sale_id and \
            picking.sale_id.purchase_order_id:
            # We try to find the associated purchase
            purchase_id = picking.sale_id.purchase_order_id.id
            domain = [('purchase_id', '=', purchase_id)]
        elif self._name == 'stock.picking.in' and picking.purchase_id and \
            picking.purchase_id.sale_order_id:
            # We try to find the associated sale
            sale_id = picking.purchase_id.sale_order_id.id
            domain = [('sale_id', '=', sale_id)]
        if domain:
            # If sale or purchase related
            # We can update the "linked" pickings
            link_picking_ids = self.search(
                cr, SUPERUSER_ID, domain, limit=1, context=context)
            if link_picking_ids:
                link_picking_id = link_picking_ids and \
                    link_picking_ids[0] or False
                self.write(cr, SUPERUSER_ID, link_picking_id, {
                    'edi_id': picking.id,
                    }, context=context)
                self.write(cr, SUPERUSER_ID, picking.id, {
                    'edi_id': link_picking_id,
                    }, context=context)
        return True

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
        sale_id = vals.get('sale_id')
        purchase_id = vals.get('purchase_id')
        company_id = vals.get('company_id')
        # If the company is defined
        # and a sale order or a purchase order too
        if company_id and (sale_id or purchase_id):
            sale_obj = self.pool.get('sale.order')
            purchase_obj = self.pool.get('purchase.order')
            stock_warehouse_obj = self.pool.get('stock.warehouse')
            data_obj = self.pool.get('ir.model.data')
            # Get the id of the record location "multi-company"
            model, location_multi_id = data_obj.get_object_reference(
                cr, uid, 'intercompany_warehouse', 'intercompany_location')
            # Getting the default warehouse of the company
            # to be able to get the warehouse default stock
            warehouse_ids = stock_warehouse_obj.search(
                cr, uid, [
                    ('company_id', '=', company_id),
                ], limit=1, context=context)
            warehouse_id = warehouse_ids and warehouse_ids[0] or False
            if warehouse_id:
                warehouse = stock_warehouse_obj.browse(
                    cr, SUPERUSER_ID, warehouse_id, context=context)
                if sale_id:
                    # If we got a sale order
                    # we update the location and destination
                    # like this:
                    # From: warehouse default stock
                    # To: multi company stock 
                    sale = sale_obj.browse(
                        cr, uid, sale_id, context=context)
                    if sale:
                        if sale.purchase_order_id:
                            vals.update({
                                'location_id': warehouse.lot_stock_id.id,
                                'location_dest_id': location_multi_id,
                            })
                elif purchase_id:
                    # If we got a purchase order
                    # we update the location and destination
                    # like this:
                    # From: multi company stock
                    # To: warehouse default stock
                    purchase = purchase_obj.browse(
                        cr, uid, purchase_id, context=context)
                    if purchase:
                        if purchase.sale_order_id:
                            vals.update({
                                'location_id': location_multi_id,
                                'location_dest_id': warehouse.lot_stock_id.id,
                            })
        return vals

    def create(self, cr, uid, vals, context=None):
        """
        Inherit the create method for the stock picking
        """
        if context is None:
            context = {}
        # Update the vals with the goods location an destination
        vals = self._update_vals_with_location_and_dest(
            cr, uid, vals=vals, context=context)
        new_id = super(stock_picking, self).create(cr, uid, vals, context=context)
        # Update the related edi picking
        self._edi_link(cr, uid, new_id, context)
        return new_id

class stock_picking_out(stock_picking):
    _name = 'stock.picking.out'
    _inherit = 'stock.picking.out'

    def _get_is_edi(self, cr, uid, ids, name, args, context=None):
        """
        This method will return if the picking is or not an edi picking
        """
        if context is None:
            context = {}
        res = {}
        for stock_picking in self.browse(cr, uid, ids, context=context):
            res[stock_picking.id] = False
            # If this picking have a related purchase to the related sale
            # or a related sale to the related purchase,
            # This picking is an edi picking
            if stock_picking.sale_id and \
                stock_picking.sale_id.purchase_order_id:
                res[stock_picking.id] = True
        return res

    _columns = {
        # TODO: make it stored on modification of sale_id
        # or sale order "purchase_order_id"
        'is_edi' : fields.function(_get_is_edi,
                                   string='Is EDI', type='boolean', store=True),
        'edi_id' : fields.many2one('stock.picking', 'EDI id'),
    }

    def action_process(self, cr, uid, ids, context=None):
        """
        Inherit the action process method.
        If this picking is an edi and the related purchase is not approved yet
        You can't validate it.
        """
        picking_id = ids and ids[0] or False
        picking = self.browse(cr, SUPERUSER_ID, picking_id, context=context)
        if picking.sale_id and picking.sale_id.purchase_order_id:
            if picking.sale_id.purchase_order_id.state == 'approved':
                return super(stock_picking_out,
                    self).action_process(cr, uid, ids, context=context)
            raise orm.except_orm(_('Error'),
                                 _('The Purchase Order (%s) '
                                   'linked with the Sale Order source '
                                   'of this Delivery Order '
                                   'is not approved yet')
                                 % (picking.sale_id.purchase_order_id.name))
        else:
            return super(stock_picking_out,
                self).action_process(cr, uid, ids, context=context)

class stock_picking_in(stock_picking):
    _name = 'stock.picking.in'
    _inherit = 'stock.picking.in'

    def _get_is_edi(self, cr, uid, ids, name, args, context=None):
        """
        This method will return if the picking is or not an edi picking
        """
        if context is None:
            context = {}
        res = {}
        for stock_picking in self.browse(cr, uid, ids, context=context):
            res[stock_picking.id] = False
            # If this picking have a related purchase to the related sale
            # or a related sale to the related purchase,
            # This picking is an edi picking
            if stock_picking.purchase_id and \
                stock_picking.purchase_id.sale_order_id:
                res[stock_picking.id] = True
        return res

    _columns = {
        # TODO: make it stored on modification of the purchase
        # or sale order "sale_order_id"
        'is_edi': fields.function(_get_is_edi,
                                  string='Is EDI', type='boolean', store=True),
        'edi_id': fields.many2one('stock.picking', 'EDI id'),
    }

    def action_process(self, cr, uid, ids, context=None):
        """
        Inherit the action process method.
        If this picking is an edi and the related picking is not done yet
        You can't validate it.
        """
        picking_id = ids and ids[0] or False
        picking = self.browse(cr, SUPERUSER_ID, picking_id, context=context)
        if picking.edi_id:
            if picking.edi_id.state == 'done':
                return super(stock_picking_in,
                    self).action_process(cr, uid, ids, context=context)
            raise orm.except_orm(_('Error'),
                                 _('The Delivery Order (%s) '
                                   'linked with this Incomming Shipment '
                                   'is not Done yet') % (picking.edi_id.name))
        else:
            return super(stock_picking_in,
                self).action_process(cr, uid, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
