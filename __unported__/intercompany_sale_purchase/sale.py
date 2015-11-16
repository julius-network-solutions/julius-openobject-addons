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

class sale_order(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'purchase_order_id': fields.many2one('purchase.order',
                                             'Purchase Order',
                                             readonly=True),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Inherit the copy method for the sale order
        to remove the default purchase order linked value
        """
        if context is None:
            context = {}
        if default is None:
            default = {}
        default.update({'purchase_order_id': False})
        return super(sale_order, self).\
            copy(cr, uid, id, default=default, context=context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        """
        Inherit the copy_data  method for the sale order
        to remove the default purchase order linked value
        """
        if context is None:
            context = {}
        if default is None:
            default = {}
        default.update({'purchase_order_id': False})
        return super(sale_order, self).\
            copy_data(cr, uid, id, default=default, context=context)

    # TODO: Check this !
    # Maybe change the way this linked purchase order is generated
    def write(self, cr, uid, ids, vals, context=None):
        """
        Inherit the write method for the sale order to create the
        linked purchase if related to an associate system company
        """
        if context is None:
            context = {}
        if isinstance(ids, (int,long)):
            ids = [ids]
        res_company_obj = self.pool.get('res.company')
        res = super(sale_order, self).\
            write(cr, uid, ids, vals, context=context)
        for so in self.browse(cr, SUPERUSER_ID, ids, context=context):
            company_ids = res_company_obj.search(
                cr, SUPERUSER_ID, [
                    '|', ('partner_id.name', '=', so.partner_id.name),
                    ('partner_id', '=', so.partner_id.id),
                ], limit=1, context=context)
            if vals.get('state') == 'manual' and \
                company_ids and not so.purchase_order_id:
                self.sale_to_purchase(cr, uid, ids, context=context)
        return res

    def _raise_edi_partner_error(self, cr, uid, context=None):
        """
        If come here, this will raise an error
        """
        if context is None:
            context = {}
        raise orm.except_orm(_('Warning'),
                             _('This customer of this sale order '
                               'is not available for EDI'))

    def _check_edi_partner(self, cr, uid, order, context=None):
        """
        This method checks if the partner is linked to a res company
        in the system. If yes, this will also checks if the warehouse
        has been well customized.
        return: the company, the partner and the warehouse 
        """
        if context is None:
            context = {}
        res_company_obj = self.pool.get('res.company')
        res_partner_obj = self.pool.get('res.partner')
        stock_warehouse_obj = self.pool.get('stock.warehouse')

        # Check if there is a company with the same name or a company
        # with directly the linked partner (the supplier company)
        company_ids = res_company_obj.search(cr, SUPERUSER_ID, [
            '|', ('partner_id.name', '=', order.partner_id.name),
            ('partner_id', '=', order.partner_id.id),
            ], limit=1, context=context)
        if not company_ids:
            self._raise_edi_partner_error(cr, uid, context)
        company_id = company_ids[0]

        # Try to find the associate "supplier"
        # If we reduce the rights and create a partner "customer"
        # and "supplier" by company for each company
        # instead of managing the companies as only 1 partner
        # for all companies, we looking for the partner which have
        # exactly the same name but defined on the customer company
        partner_ids = res_partner_obj.search(cr, SUPERUSER_ID, [
            '|', '&', ('name', '=', order.company_id.name),
            ('company_id', '=', company_id),
            '&', ('id', '=', order.company_id.partner_id.id),
            ('company_id', '=', False),
            ], limit=1, context=context)
        partner_id = partner_ids[0]
        if not partner_id:   
            self._raise_edi_partner_error(cr, uid, context)

        # To be able to continue we need to get
        # the default warehouse of the linked company
        warehouse_ids = stock_warehouse_obj.search(cr, SUPERUSER_ID, [
            ('company_id', '=', company_id),
            ], limit=1, context=context)
        if not warehouse_ids:
            raise orm.except_orm(_('Warning'),
                                 _('This linked company of '
                                   'this customer doesn\'t have '
                                   'any warehouse defined.\n'
                                   'Please ask the administrator '
                                   'to create one to be able '
                                   'to manage EDI.'))
        warehouse_id = warehouse_ids[0]
        return company_id, partner_id, warehouse_id

    def _get_vals_for_edi_purchase(self, cr, uid, order,
                                   company_id, partner_id,
                                   warehouse_id, pricelist_id,
                                   context=None):
        """
        This method will return the defaults values to create the
        new purchase order linked to this sale order
        """
        if context is None:
            context = {}
        stock_warehouse_obj = self.pool.get('stock.warehouse')
        ir_values = self.pool.get('ir.values')
        partner_obj = self.pool.get('res.partner')

        # Get the warehouse datas
        warehouse = stock_warehouse_obj.\
            browse(cr, SUPERUSER_ID, warehouse_id, context=context)

        # Get default values
        invoice_method = ir_values.get_default(
            cr, uid, 'purchase.order', 'invoice_method') or 'order'
        partner_address_id = partner_obj.\
            address_get(cr, SUPERUSER_ID, [partner_id], ['default'])['default']

        # Return the values
        return {
            'state': 'draft',
            'partner_id': partner_id,
            'partner_address_id': partner_address_id,
            'company_id': company_id,
            'origin': order.name,
            'payment_term_id': order.payment_term.id,
            'fiscal_position': order.fiscal_position.id,
            'date_order': order.date_order,
            'pricelist_id': pricelist_id,
            'warehouse_id': warehouse_id,
            'location_id': warehouse.lot_stock_id.id,
            'invoice_method': invoice_method,
            'sale_order_id': order.id,
        }

    def _get_vals_for_edi_purchase_line(self, cr, uid, line,
                                        purchase_id, partner_id,
                                        pricelist_id, company_id,
                                        context=None):
        """
        This method will return the defaults values to create the
        new purchase order lines linked to this sale order
        """
        if context is None:
            context = {}
        purchase_line_obj = self.pool.get('purchase.order.line')

        # launch the onchange method to fill all the fields
        # like if it was done by a user manually
        res = purchase_line_obj.onchange_product_id(
            cr, SUPERUSER_ID, [], pricelist_id, line.product_id.id,
            qty=line.product_uom_qty, uom_id=False,
            partner_id=partner_id, date_order=line.order_id.date_order,
            fiscal_position_id=False, context=context)
        vals = res.get('value', {})

        # Add the required info not added by the onchange
        vals.update({
            'order_id': purchase_id,
            'price_unit': line.price_unit,
            'name': line.name,
            'taxes_id': [(6, 0, [])],
            'product_id': False,
            'type': 'make_to_order',
            })

        # For taxes, this is a little be tricky
        # because we need to get only default taxes
        # of the linked company not all default taxes
        # this is the reason why we don't use
        # the "resolve_2many_commands" method
        taxes = []
        for tax in line.product_id.supplier_taxes_id:
            if tax.company_id.id == company_id:
                taxes.append(tax.id)
        if taxes:
            vals.update({
                'taxes_id': [(6, 0, taxes)],
                })

        # If the linked product is not specific to a company
        # or linked to the supplier company we can return the
        # product_id value, else we let the product_id empty
        if not line.product_id.company_id or \
            line.product_id.company_id == company_id:
            vals.update({
                'product_id': line.product_id.id,
                })
        return vals

    def _get_purchase_pricelist(self, cr, uid,
                                order, partner_id, context=None):
        """
        This method will get the supplier list price
        """
        if context is None:
            context = {}
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id, context=context)
        pricelist_id = partner and \
            partner.property_product_pricelist_purchase and \
            partner.property_product_pricelist_purchase.id or False
        return pricelist_id or order.company_id.partner_id.\
            property_product_pricelist_purchase.id

    def sale_to_purchase(self, cr, uid, ids, context=None):
        """
        This method will create the linked purchase order
        """
        if context is None:
            context = {}

        purchase_order_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')

        # Creation of one purchase order by sale if it needs to
        for order in self.browse(cr, SUPERUSER_ID, ids, context=context):
            # If there is already a linked purchase order
            # raise an error !
            if order.purchase_order_id:
                raise orm.except_orm(_('Warning!'),
                                     _('You already had a purchase order '
                                       'for this sale order.\n'
                                       'Please delete the %s '
                                       'if you want to create a new one')
                                     % (order.purchase_order_id.name))

            # Get the company linked, the supplier and company warehouse 
            company_id, partner_id, warehouse_id = self.\
                _check_edi_partner(cr, SUPERUSER_ID, order, context=context)

            # Get the good purchase list price
            pricelist_id = self.\
                _get_purchase_pricelist(cr, SUPERUSER_ID, order,
                                        partner_id, context=context)

            # Get the default values to create the linked purchase order
            vals = self._get_vals_for_edi_purchase(cr, SUPERUSER_ID, order,
                                                   company_id, partner_id,
                                                   warehouse_id,
                                                   pricelist_id,
                                                   context=context)

            # Create the linked purchase order without lines
            purchase_id = purchase_order_obj.\
                create(cr, SUPERUSER_ID, vals, context=context)

            # Read the linked purchase order name
            purchase = purchase_order_obj.read(
                cr, SUPERUSER_ID, purchase_id, ['name'], context=context)

            # Update the current sale order with the ref name
            # and the linked purchase order
            self.write(cr, SUPERUSER_ID, [order.id], {
                'client_order_ref': purchase['name'],
                'purchase_order_id': purchase_id,
                }, context=context)

            # Creation of the Purchase order lines
            for line in order.order_line:
                # Get the default values one by one.
                vals = self._get_vals_for_edi_purchase_line(
                    cr, SUPERUSER_ID, line, purchase_id, partner_id,
                    pricelist_id, company_id, context=context)
                # Create the line
                purchase_line_obj.create(cr, SUPERUSER_ID,
                                         vals, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
