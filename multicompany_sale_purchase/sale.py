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
    
    ######################################################
    ### TODO : Mgt of access rights for Multi Company
    ######################################################
    def sale_to_purchase(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        purchase_order_obj = self.pool.get('purchase.order')
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        res_company_obj = self.pool.get('res.company')
        purchase_order_tax_obj = self.pool.get('purchase.order.tax')
        #Creation of the Purchase Order
        for so in self.browse(cr ,uid, ids, context=context):
            company_id = res_company_obj.search(cr, uid, [('partner_id','=',so.partner_id.id)], context=context)
            vals = {
                'state' : 'draft',
                'partner_id' : so.company_id.partner_id.id,
                'company_id' : company_id[0],
                'origin' : so.name,
                'payment_term_id' : so.payment_term.id,
                'fiscal_position' : so.fiscal_position.id,
                'date_order' : so.date_order,
                'pricelist_id' : so.company_id.partner_id.property_product_pricelist.id,
                'location_id' : 12, #Pop up
                'invoice_method' : 'order',
            }
            po_id = purchase_order_obj.create(cr, uid, vals, context=context)
            po = purchase_order_obj.browse(cr , uid, po_id, context=context)
            self.write(cr, uid, so.id, {'client_order_ref': po.name}, context = context)
            #Creation of the Purchase Order Line
            for line in so.order_line:
                values = {
                      'product_id' : line.product_id.id,
                      'name' : line.name,
                      'product_qty' : line.product_uom_qty,
                      'price_unit' : line.price_unit,
                      'order_id' : po_id,
                      'product_uom' : 1, #Hardcode..
                      'date_planned': so.date_order #Pop up
                }
                pol_id = purchase_order_line_obj.create(cr, uid, values, context=context)
#                 for taxe in line.taxes_id:
#                     sale_order_tax_obj.create(cr, uid, {'ord_id' : pol_id,'tax_id':taxe.id}, context=context)
        return True