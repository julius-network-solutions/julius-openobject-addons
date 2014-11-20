# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
###############################################################################

## ODOO LIB ##
from openerp import models, api, fields
from openerp.tools.translate import _

class product_packaging(models.Model):
    _inherit = "product.packaging"

    uom_id = fields.Many2one('product.uom', 'Unit of measure')

class stock_picking(models.Model):
    _inherit = "stock.picking"
    
    @api.model
    def process_barcode_from_ui(self, picking_id, barcode_str, visible_op_ids):
        # Initialization
        packaging_obj = self.env['product.packaging']
        product_obj = self.env['product.product']
        stock_operation_obj = self.env['stock.pack.operation']
        answer = {'filter_loc': False, 'operation_id': False}
        
        # Check if the barcode correspond to a packaging type
        matching_packaging_ids = packaging_obj.search([('ean', '=', barcode_str)], limit=1)
        for matching_packaging in matching_packaging_ids:
            product = product_obj.search([('product_tmpl_id','=',matching_packaging.product_tmpl_id.id)])
            if matching_packaging.uom_id:
                mutli_qty = 1 / matching_packaging.uom_id.factor
                op_id = stock_operation_obj._search_and_multi_increment(picking_id, 
                                                                        [('product_id', '=', product.id)], 
                                                                        filter_visible=True, mutli_qty=mutli_qty,
                                                                        visible_op_ids=visible_op_ids, increment=True)
                answer['operation_id'] = op_id
            return answer
        
        # Default Process
        result = super(stock_picking, self).process_barcode_from_ui(picking_id, barcode_str, visible_op_ids)
        return result

class stock_pack_operation(models.Model):
    _inherit = "stock.pack.operation"
            
    @api.model
    def _search_and_multi_increment(self, picking_id, domain, filter_visible=False, mutli_qty=1, visible_op_ids=False, increment=True):
        '''Search for an operation with given 'domain' in a picking, if it exists increment the qty (+mutli_qty) otherwise create it
        :param domain: list of tuple directly reusable as a domain
        context can receive a key 'current_package_id' with the package to consider for this operation
        returns operation id
        '''
        #if current_package_id is given in the context, we increase the number of items in this package
        package_clause = [('result_package_id', '=', self._context.get('current_package_id', False))]
        existing_operation_ids = self.search([('picking_id', '=', picking_id)] + domain + package_clause)
        todo_operation_ids = []
        if existing_operation_ids:
            if filter_visible:
                todo_operation_ids = [val for val in existing_operation_ids if val.id in visible_op_ids]
            else:
                todo_operation_ids = existing_operation_ids
        if todo_operation_ids:
            #existing operation found for the given domain and picking => increment its quantity
            operation = todo_operation_ids[0]
            qty = operation.qty_done
            if increment:
                qty += mutli_qty
            else:
                qty -= mutli_qty if qty >= mutli_qty else 0
                if qty == 0 and op_obj.product_qty == 0:
                    #we have a line with 0 qty set, so delete it
                    operation.unlink()
                    return False
            operation.write({'qty_done': qty})
        else:
            #no existing operation found for the given domain and picking => create a new one
            picking_obj = self.env['stock.picking']
            picking = picking_obj.browse(picking_id)
            values = {
                'picking_id': picking_id,
                'product_qty': 0,
                'location_id': picking.location_id.id, 
                'location_dest_id': picking.location_dest_id.id,
                'qty_done': mutli_qty,
                }
            for key in domain:
                var_name, dummy, value = key
                uom_id = False
                if var_name == 'product_id':
                    uom_id = self.env['product.product'].browse(value).uom_id.id
                update_dict = {var_name: value}
                if uom_id:
                    update_dict['product_uom_id'] = uom_id
                values.update(update_dict)
            operation = self.create(values)
        return operation.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
