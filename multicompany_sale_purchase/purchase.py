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



class purchase_order(orm.Model):
    _inherit = "purchase.order"
    
    ######################################################
    ### TODO : Mgt of access rights for Multi Company
    ######################################################
    def purchase_to_sale(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_order_obj = self.pool.get('sale.order')
        sale_order_line_obj = self.pool.get('sale.order.line')
        res_company_obj = self.pool.get('res.company')
        sale_order_tax_obj = self.pool.get('sale.order.tax')
        #Creation of the Sale Order
        for po in self.browse(cr ,uid, ids, context=context):
            company_id = res_company_obj.search(cr, uid, [('partner_id','=',po.partner_id.id)], context=context)
            vals = {
                'state' : 'draft',
                'partner_id' : po.company_id.partner_id.id,
                'partner_invoice_id' : po.company_id.partner_id.id,
                'partner_shipping_id' : po.company_id.partner_id.id,
                'company_id' : company_id[0],
                'origin' : po.name,
                'payment_term' : po.payment_term_id.id,
                'fiscal_position' : po.fiscal_position.id,
                'date_order' : po.date_order,
                'pricelist_id' : po.company_id.partner_id.property_product_pricelist.id,
                'picking_policy' : 'direct',
                'order_policy' : 'manual',
            }
            so_id = sale_order_obj.create(cr, uid, vals, context=context)
            so = sale_order_obj.browse(cr , uid, so_id, context=context)
            self.write(cr, uid, po.id, {'partner_ref': so.name}, context = context)
            #Creation of the Sale Order Line
            for line in po.order_line:
                values = {
                      'product_id' : line.product_id.id,
                      'name' : line.name,
                      'product_uom_qty' : line.product_qty,
                      'price_unit' : line.price_unit,
                      'order_id' : so_id,
                }
                sol_id = sale_order_line_obj.create(cr, uid, values, context=context)
#                 for taxe in line.taxes_id:
#                     sale_order_tax_obj.create(cr, uid, {'order_line_id' : sol_id,'tax_id':taxe.id}, context=context)
        return True
    
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: