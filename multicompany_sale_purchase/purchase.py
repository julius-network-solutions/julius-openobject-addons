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

class purchase_order(orm.Model):
    _inherit = "purchase.order"
    
    _columns = {
        'sale_order_id' : fields.many2one('sale.order','Sale Order',readonly=True)
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int,long)):
            ids = [ids]
        res_company_obj = self.pool.get('res.company')
        res = super(purchase_order, self).write(cr, uid, ids, vals, context=context)
        for so in self.browse(cr, 1, ids, context=context):
            company_id = res_company_obj.search(cr, 1, [('partner_id.name','=',so.partner_id.name)], context=context)
            if vals.get('state') == 'approved' and company_id and not so.sale_order_id:
                self.purchase_to_sale(cr, uid, ids, context=context)
        return res
    
    
    def purchase_to_sale(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_order_obj = self.pool.get('sale.order')
        sale_order_line_obj = self.pool.get('sale.order.line')
        res_company_obj = self.pool.get('res.company')
        res_partner_obj = self.pool.get('res.partner')
        stock_warehouse_obj = self.pool.get('stock.warehouse')
        sale_order_tax_obj = self.pool.get('sale.order.tax')
        sale_shop_obj = self.pool.get('sale.shop')
        account_tax_obj = self.pool.get('account.tax')
        #Creation of the Sale Order
        for po in self.browse(cr ,1, ids, context=context):
            if po.sale_order_id:
                raise orm.except_orm(_('Warning!'),
                                    _('You already had a sale order for this purchase order '
                                      'Please delete the %s if you want to create a new one')
                                    % (po.sale_order_id.name))
            company_id = res_company_obj.search(cr, 1, [('partner_id.name','=',po.partner_id.name)], context=context)
            if not company_id:
                raise orm.except_orm(_('Warning'),
                                     _('This partner is not avaible for EDI')) 
            partner_id = res_partner_obj.search(cr, 1, [('name','=',po.company_id.name),('company_id','=',company_id)], context=context)
            if not partner_id:                
                raise orm.except_orm(_('Warning'),
                                     _('This partner is not avaible for EDI'))
            sale_shop_id = sale_shop_obj.search(cr, 1, [('company_id','=',company_id)], context=context)
            if not sale_shop_id:                
                raise orm.except_orm(_('Warning'),
                                     _('This partner is not avaible for EDI'))
            warehouse_id = stock_warehouse_obj.search(cr, 1, [('company_id','=',company_id)], context=context)
            if not warehouse_id:                
                raise orm.except_orm(_('Warning'),
                                     _('This partner is not avaible for EDI'))
            warehouse = stock_warehouse_obj.browse(cr, 1, warehouse_id[0],context=context)
            vals = {
                'state' : 'draft',
                'partner_id' : partner_id[0],
                'partner_invoice_id' : partner_id[0],
                'partner_shipping_id' : partner_id[0],
                'company_id' : company_id[0],
                'origin' : po.name,
                'payment_term' : po.payment_term_id.id,
                'fiscal_position' : po.fiscal_position.id,
                'date_order' : po.date_order,
                'pricelist_id' : po.company_id.partner_id.property_product_pricelist.id,
                'picking_policy' : 'direct',
                'order_policy' : 'manual',
                'shop_id' : sale_shop_id[0],
                'purchase_order_id' : po.id, 
            }
            so_id = sale_order_obj.create(cr, 1, vals, context=context)
            so = sale_order_obj.browse(cr , 1, so_id, context=context)
            self.write(cr, 1, [po.id], {'partner_ref': so.name, 'sale_order_id': so_id}, context = context)
            #Creation of the Sale Order Line
            for line in po.order_line:
                res = sale_order_line_obj.product_id_change(cr, 1, ids,
                    po.company_id.partner_id.property_product_pricelist.id, line.product_id.id, 
                    qty=line.product_qty, uom=False, qty_uos=False, uos=False,
                    name=line.name, partner_id=partner_id[0], lang=False, update_tax=False,
                    date_order=po.date_order, packaging=False, fiscal_position=po.fiscal_position.id,
                    flag=False, context=context)
                res['value'].update({'order_id' : so_id, 'price_unit' : line.price_unit, 'product_uom_qty' : line.product_qty,'name': line.name})
                taxes = []
                for tax in line.product_id.taxes_id:
                    if tax.company_id.id == company_id[0]:
                        taxes.append(tax.id)
                if taxes:
                    res['value'].update({'tax_id': [(6, 0, taxes)]})
                if not line.product_id.company_id or line.product_id.company_id == company_id:
                    res['value'].update({'product_id' : line.product_id.id})
                sol_id = sale_order_line_obj.create(cr, 1, res['value'], context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
