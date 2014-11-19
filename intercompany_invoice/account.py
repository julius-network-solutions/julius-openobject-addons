# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
###############################################################################

from openerp import models, api, fields, _
from openerp.exceptions import Warning

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    customer_invoice_id = fields.Many2one('account.invoice',
                                          'Customer Invoice', readonly=True)
    supplier_invoice_id = fields.Many2one('account.invoice',
                                          'Supplier Invoice', readonly=True)
    
    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['supplier_invoice_id'] = False
        return super(account_invoice, self).copy(default)
    
    def copy_data(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        default['supplier_invoice_id'] = False
        return super(account_invoice, self).\
            copy_data(cr, uid, id, default=default, context=context)

    @api.multi
    def write(self, vals):
        res_company_obj = self.env['res.company']
        res = super(account_invoice, self).write(vals)
        for ci in self:
            company_ids = res_company_obj.sudo().search(
                [('partner_id', '=', ci.partner_id.id)], limit=1)
            if vals.get('state') == 'open' and \
                company_ids and not ci.supplier_invoice_id:
                self.customer_to_supplier()
        return res

    @api.multi
    def _check_intercompany_partner(self):
        res_company_obj = self.env['res.company']
        res_partner_obj = self.env['res.partner']

        company_id = res_company_obj.sudo().search(
            [('partner_id', '=', self.partner_id.id)], limit=1)

        partner_id = res_partner_obj.sudo().search(
            [('id', '=', self.company_id.partner_id.id),
            ('company_id', '=', False),], limit=1)
        
        if not partner_id:   
            Warning(_('Intercompany Partner not found !'))
        return company_id, partner_id
    
    @api.multi
    def _get_vals_for_supplier_invoice(self, company, partner):
        journal_obj = self.env['account.journal']
        prop = self.env['ir.property']
        
        journal = journal_obj.sudo().\
            search([
                    ('type', '=', 'purchase'),
                    ('company_id', '=', company.id),
#                     ('currency', '=', self.currency_id.id),
                    ], limit=1)
        if not journal:
            raise Warning(_('Impossible to generate the linked invoice to ' \
                            '%s, There is no purchase journal ' \
                            'defined.' %company.name))
        pay_account = partner.property_account_payable
        if partner.property_account_payable.company_id and \
            partner.property_account_payable.company_id.id != company.id:
            pay_dom = [
                       ('name', '=', 'property_account_payable'),
                       ('company_id', '=', company.id),
                       ]
            res_dom = [
                       ('res_id', '=', 'res.partner,%s' % partner_id),
                       ]
            pay_prop = prop.search(pay_dom + res_dom) or prop.search(pay_dom)
            if pay_prop:
                pay_account = pay_prop.get_by_record(pay_prop)
        return {
            'state': 'draft',
            'partner_id': partner.id,
            'journal_id': journal.id,
            'account_id': pay_account.id,
            'company_id': company.id,
            'origin': self.name,
            'payment_term_id': self.payment_term.id or False,
            'fiscal_position': self.fiscal_position.id or False,
            'date_invoice': self.date_invoice or False,
            'date_due': self.date_due or False,
            'customer_invoice_id': self.id,
            'type': 'in_invoice',
        }

    @api.multi
    def _get_vals_for_supplier_invoice_line(self, supplier_invoice, line, company, partner):  
        if line.product_id:
            res = line.sudo().\
                product_id_change(line.product_id.id, line.uos_id.id,
                                  line.quantity, line.name,
                                  supplier_invoice.type, partner.id,
                                  supplier_invoice.fiscal_position.id,
                                  line.price_unit,
                                  supplier_invoice.currency_id.id,
                                  company_id=company.id)
            vals = res.get('value', {})
            if not line.product_id.company_id:
                vals.update({'product_id': line.product_id.id})
            vals.update({
                'invoice_id': supplier_invoice.id,
                'name': line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                })
        else:
            account = line._default_account()
            vals = {
                'invoice_id': supplier_invoice.id,
                'name': line.name,
                'account_id': account.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
            }
        return vals

    @api.multi
    @api.depends('invoice_line')
    def customer_to_supplier(self):
        """
        This method will create the linked supplier invoice
        """

        account_invoice_obj = self.env['account.invoice']
        account_invoice_line_obj = self.env['account.invoice.line']

        for invoice in self:
            if invoice.supplier_invoice_id:
                raise Warning(_('You already had a supplier invoice '
                                'for this customer invoice.\n'
                                'Please delete the %s '
                                'if you want to create a new one')
                                % (invoice.supplier_invoice_id.name))

            company, partner = self.sudo()._check_intercompany_partner()

            vals = self.sudo()._get_vals_for_supplier_invoice(company, partner)
            supplier_invoice = self.sudo().create(vals)
            self.write({'supplier_invoice_id': supplier_invoice.id})
            for line in invoice.invoice_line:
                vals = self.sudo().\
                    _get_vals_for_supplier_invoice_line(supplier_invoice, line,
                                                        company, partner)
                account_invoice_line_obj.sudo().create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
