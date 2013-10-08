# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from openerp import netsvc
from openerp.osv import fields, orm
from openerp.tools.translate import _


class sale_order(orm.Model):
    _inherit = "sale.order"
    
    _columns = {
        'purchase_order_id' : fields.many2one('purchase.order','Purchase Order',readonly=True)
    }
    ######################################################
    ### TODO : Mgt of access rights for Multi Company
    ######################################################
    def sale_to_purchase(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        purchase_order_obj = self.pool.get('purchase.order')
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        res_company_obj = self.pool.get('res.company')
        res_partner_obj = self.pool.get('res.partner')
        stock_warehouse_obj = self.pool.get('stock.warehouse')
        purchase_order_tax_obj = self.pool.get('purchase.order.tax')
        account_tax_obj = self.pool.get('account.tax')
        #Creation of the Purchase Order
        for so in self.browse(cr ,1, ids, context=context):
            company_id = res_company_obj.search(cr, 1, [('partner_id.name','=',so.partner_id.name)], context=context)
            partner_id = res_partner_obj.search(cr, 1, [('name','=',so.company_id.name),('company_id','=',company_id)], context=context)
            warehouse_id = stock_warehouse_obj.search(cr, 1, [('company_id','=',company_id)], context=context)
            warehouse = stock_warehouse_obj.browse(cr, 1, warehouse_id[0],context=context)
            vals = {
                'state' : 'draft',
                'partner_id' : partner_id[0],
                'company_id' : company_id[0],
                'origin' : so.name,
                'payment_term_id' : so.payment_term.id,
                'fiscal_position' : so.fiscal_position.id,
                'date_order' : so.date_order,
                'pricelist_id' : so.company_id.partner_id.property_product_pricelist.id,
                'warehouse_id' : warehouse_id[0],
                'location_id' : warehouse.lot_output_id.id,
                'invoice_method' : 'order',
            }
            po_id = purchase_order_obj.create(cr, 1, vals, context=context)
            po = purchase_order_obj.browse(cr , 1, po_id, context=context)
            self.write(cr, 1, so.id, {'client_order_ref': po.name,'purchase_order_id': po_id}, context = context)
            #Creation of the Purchase Order Line
            for line in so.order_line:
                res = purchase_order_line_obj.onchange_product_id(cr, 1, [], so.company_id.partner_id.property_product_pricelist.id, line.product_id.id, 
                    qty=line.product_uom_qty, uom_id=False, partner_id=partner_id[0], date_order=so.date_order,
                    fiscal_position_id=False, context=context)
                res['value'].update({'order_id' : po_id})
                taxes = []
                for tax in line.product_id.supplier_taxes_id:
                    if tax.company_id.id == company_id[0]:
                        taxes.append(tax.id)
                if taxes:
                    res['value'].update({'taxes_id': [(6, 0, taxes)]})
                if not line.product_id.company_id or line.product_id.company_id == company_id:
                    res['value'].update({'product_id' : line.product_id.id})
                pol_id = purchase_order_line_obj.create(cr, 1, res['value'], context=context)
        return True