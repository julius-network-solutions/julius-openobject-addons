# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, api, fields, _
from openerp.exceptions import Warning

class tax_certificate(models.Model):
    _name = "tax.certificate"
    _description ='Tax certificate'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        certificate_type = context.get('type', 'out_certificate')
        return certificate_type
    
    def _get_currency(self, cr, uid, context=None):
        user_obj = self.pool.get('res.users')
        currency_obj = self.pool.get('res.currency')
        user = user_obj.browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return currency.search(cr, uid, [('rate', '=', 1.0)])[0]

    name = fields.Char('Description', size=128, readonly=True,
                       states={'draft':[('readonly',False)]})
    type = fields.Selection([
                             ('out_certificate', 'Customer Certificate'),
                             ('in_certificate', 'Supplier Certificate')
                             ], 'Type', readonly=True)
    number = fields.Char('Certificate Number', size=32, readonly=True,
                         copy=False,
                         help="Unique number of the certificate, computed " \
                         "automatically when the certificate is validated.")
    partner_id = fields.Many2one('res.partner', 'Partner',
                                 required=True, readonly=True,
                                 states={'draft':[('readonly',False)]})
    partner_address_id = fields.Many2one('res.partner',
                                         'Partner address', required=True,
                                         readonly=True,
                                         states={'draft':[('readonly',False)]})
    salesman_id = fields.Many2one('res.users', 'Salesman',
                                  readonly=True,
                                  states={'draft':[('readonly',False)]})
    amount_untaxed = fields.Float('Amount untaxed',
                                  readonly=True,
                                  states={'draft':[('readonly',False)]},
                                  track_visibility='always')
    amount_tax = fields.Float('Amount tax',
                              readonly=True,
                              states={'draft':[('readonly',False)]},
                              track_visibility='always')
    amount_total = fields.Float('Amount total',
                                readonly=True,
                                states={'draft':[('readonly',False)]},
                                track_visibility='always')
    payment_done = fields.Float('Payment Cesu Done',
                                readonly=True,
                                states={'draft':[('readonly',False)]})
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  readonly=True,
                                  states={'draft':[('readonly',False)]})
    state = fields.Selection([
                              ('draft', 'Draft'),
                              ('open', 'Open'),
                              ('cancel', 'Cancelled')
                              ], 'State', readonly=True,
                             track_visibility='onchange')
    invoice_ids = fields.Many2many('account.invoice',
                                   'account_invoice_certificate_rel',
                                   'invoice_id', 'certificate_id',
                                   string='Invoices',
                                   readonly=True,
                                   states={'draft':[('readonly',False)]})
    invoice_line_ids = fields.Many2many('account.invoice.line',
                                        'account_invoice_line_certificate_rel',
                                        'line_id', 'certificate_id',
                                        string='Invoice lines',
                                        readonly=True,
                                        states={'draft':[('readonly',False)]})
    date = fields.Date('Date Certificate',
                       readonly=True,
                       states={'draft':[('readonly',False)]},
                       help="Keep empty to use the current date")
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscalyear',
                                    readonly=True,
                                    states={'draft':[('readonly',False)]},
                                    required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company'].\
                                    _company_default_get('tax.certificate'))
    line_ids = fields.One2many('tax.certificate.line', 'certificate_id',
                               'Tax certificate lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    notes = fields.Text('Notes')
    origin = fields.Char('Origin', size=32, readonly=True,
                         states={'draft': [('readonly', False)]})

    _defaults = {
        'state': 'draft',
        'type': _get_type,
        'currency_id': _get_currency,
    }

    @api.onchange('amount_untaxed', 'amount_tax')
    def onchange_amounts(self):
        self.amount_total = (self.amount_untaxed or 0) + (self.amount_tax or 0)

    @api.onchange('partner_id')
    def onchange_partner(self):
        user_id = False
        partner = self.partner_id
        if partner:
            if partner.user_id:
                user_id = partner.user_id.id
            get_adresses = partner.address_get(['invoice'])
            self.partner_address_id = get_adresses.get('invoice', partner.id)
        else:
            self.partner_address_id = False
        self.user_id = user_id

    @api.model
    def get_number(self, type='out_certificate'):
        seq_obj = self.env['ir.sequence']
        return seq_obj.next_by_code('tax.certificate.' + type)

    @api.multi
    def validate_certificate(self):
        today = fields.Date.context_today(self)
        default_datas = {
            'state' : 'open',
        }
        for certificate in self:
            if certificate.state == 'draft':
                datas = default_datas.copy()
                if not self.number:
                    self.number = self.get_number(certificate.type)
                if not certificate.date:
                    datas['date'] = today
                certificate.write(datas)

    @api.multi
    def cancel_certificate(self):
        for certificate in self:
            if certificate.state in ('draft', 'open'):
                datas = {
                    'state': 'cancel',
                    'date': False,
                }
                certificate.write(datas)

    @api.multi
    def draft_certificate(self):
        for certificate in self:
            if certificate.state == 'cancel':
                certificate.state = 'draft'

    @api.one
    def _compute_data(self):
        tax_obj = self.env['account.tax']
        total_untaxed = 0
        total_tax = 0
        total = 0
        product_ids = []
        for invoice_line in self.invoice_line_ids:
            if invoice_line.invoice_id.reconciled:
                if product_ids and invoice_line.product_id.id in \
                    product_ids or not product_ids:
                    total_untaxed += invoice_line.price_subtotal
                    price_unit = invoice_line.price_unit * \
                        (1-(invoice_line.discount or 0.0)/100.0)
                    quantity = invoice_line.quantity
                    taxes = invoice_line.invoice_line_tax_id
                    partner = invoice_line.invoice_id.partner_id
                    product = invoice_line.product_id.id
                    for tax in taxes.compute_all(price_unit, quantity,
                                                 partner.id,
                                                 product)['taxes']:
                        total_tax += tax['amount']
        total += total_untaxed + total_tax
        return {
            'amount_untaxed': total_untaxed,
            'amount_tax': total_tax,
            'amount_total': total
            }

    @api.multi
    def update_amount(self):
        for certificate in self:
            vals = certificate._compute_data()
            if isinstance(vals, list):
                vals = vals and vals[0] or {}
            certificate.write(vals)

    @api.multi
    def compute_lines(self):
        line_obj = self.env['tax.certificate.line']
        account_analytic_line_obj = self.env['account.analytic.line']
        period_obj = self.env['account.period']
        for certificate in self:
            lines_to_del = line_obj.search([('certificate_id', '=', certificate.id)])
            analytic_account_ids = []
            for x in certificate.invoice_line_ids:
                if x.account_analytic_id.id and x.account_analytic_id.id not in analytic_account_ids:
                    analytic_account_ids.append(x.account_analytic_id.id)
            year = certificate.fiscalyear_id
            date_start = year.date_start
            date_stop = year.date_stop
            analytic_lines = account_analytic_line_obj.\
                search([
                        ('account_id', 'in', analytic_account_ids),
                        ('date', '>=', date_start),
                        ('date', '<=', date_stop)
                        ])
            for analytic_line in analytic_lines:
                period = False
                invoice = analytic_line.invoice_id
                if invoice:
                    #TODO: this is specific to a customer
#                     and analytic_line.product_id.id not in [1362,1394,1493]:
                    period = invoice.period_id
                else:
                    date = analytic_line.date
                    periods = period_obj.\
                        search([
                                ('fiscalyear_id', '=', year.id),
                                ('date_start', '<=', date),
                                ('date_stop', '>=', date)
                                ], limit=1)
                    if periods:
                        period = periods[0]
                if analytic_line:
                    vals = {
                        'certificate_id': certificate.id,
                        'analytic_id': analytic_line.id,
                        'period_id': period and period.id or False,
                        'product_id': analytic_line.product_id and \
                            analytic_line.product_id.id or False,
                    }
                    line_obj.create(vals)
            lines_to_del.unlink()

    @api.multi
    def unlink(self):
        for invoice in self:
            if invoice.state not in ('draft', 'cancel'):
                raise Warning(_('You cannot delete an certificate ' \
                                'which is not draft or cancelled.'))
        return super(tax_certificate, self).unlink()

class tax_certificate_line(models.Model):
    _name = "tax.certificate.line"
    _description ='Tax Certificate lines'

    certificate_id = fields.Many2one('tax.certificate', 'Certificate',
                                     required=True, ondelete='cascade')
    period_id = fields.Many2one('account.period', 'Period')
    analytic_id = fields.Many2one('account.analytic.line',
                                  'Account analytic line')
    product_id = fields.Many2one('product.product', 'Product')

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.returns('tax.certificate')
    def create_certificate(self, fiscalyear, product_ids=None):
        if product_ids is None:
            product_ids = []
        today = fields.Date.context_today(self)
        partners = self.env['res.partner']
        lines = self.env['account.invoice.line']
        certificates = certificate_obj = self.env['tax.certificate']
        for invoice in self:
            partner = invoice.partner_id
            if partner.parent_id:
                partner = partner.parent_id
            if not partner in partners:
                partners += partner
        for partner in partners:
            partner_address = partner.\
                address_get(['invoice']).get('invoice', partner)
            salesman_id = partner.user_id and partner.user_id.id or False
            partner_invoice_ids = []
            for invoice in self:
                if invoice.partner_id.id == partner.id or \
                    invoice.partner_id.parent_id and \
                    invoice.partner_id.parent_id.id == partner.id:
                    partner_invoice_ids.append(invoice.id)
            domain = [('invoice_id', 'in', partner_invoice_ids)]
            if product_ids:
                domain.append(('product_id', 'in', product_ids))
            partner_invoice_line_ids = lines.search(domain)
            vals = {
                'name': ' - '.join([today,fiscalyear.name,partner.name]),
                'partner_id': partner.id,
                'fiscalyear_id': fiscalyear.id,
                'partner_address_id': partner_address,
                'invoice_ids': [(6, 0, partner_invoice_ids)],
                'invoice_line_ids': [(6, 0, partner_invoice_line_ids.ids)],
                'salesman_id': salesman_id,
            }
            if partner.company_id:
                vals.update({'company_id': partner.company_id.id})
            certificates += certificate_obj.create(vals)
        if certificates:
            certificates.compute_lines()
            certificates.update_amount()
        return certificates

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
