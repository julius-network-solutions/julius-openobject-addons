# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions (<http://www.julius.fr/>) contact@julius.fr
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
#################################################################################

from openerp.osv import fields,osv
from openerp import tools
from openerp.tools import config
#import time
from mx import DateTime

class tax_certificate(osv.osv):
    _name = "tax.certificate"
    _description ='Tax certificate'
    
    def _get_type(self, cr, uid, context = None):
        if context is None:
            context = {}
        certificate_type = context.get('type', 'out_certificate')
        return certificate_type
    
    def _get_currency(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return self.pool.get('res.currency').search(cr, uid, [('rate','=',1.0)])[0]

    def _get_line_ids(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        list_ids = []
        line_obj = self.pool.get('account.invoice.line')
        records = self.browse(cr, uid, ids, context)
        for record in records :
            for invoice in record.invoice_ids:
                list_ids.append(invoice.id)
            line_ids = line_obj.search(cr, uid, [('invoice_id','in',list_ids)])
            result[record.id] = line_ids
        return result
    
#    def _get_total(self, cr, uid, ids, field_name, arg, context={}):
#        res = {}
##        uom_obj = self.pool.get('product.uom')
#        records = self.browse(cr, uid, ids, context)
#        for record in records :
#            res[record.id] = {
#                  'amount_untaxed' : 0.0,
#                  'amount_tax' : 0.0,
#                  'amount_total' : 0.0,
#                }
#            for invoice in record.invoice_ids:
#                res[record.id]['amount_untaxed'] += invoice.amount_untaxed
#                res[record.id]['amount_tax'] += invoice.amount_tax
#                res[record.id]['amount_total'] += invoice.amount_total
#        return res
    
    def _get_names(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        records = self.browse(cr, uid, ids, context)
        for record in records :
            res[record.id] = {
              'parent' : '',
              'parent_dest' : '',
            }
            if record.parent_address_id:
                parent_name = record.parent_address_id.partner_id.name
                parent_first = record.parent_address_id.partner_id.firstname
                if parent_first :
                    res[record.id]['parent'] += parent_first + ' '
                if parent_name :
                    res[record.id]['parent'] += parent_name
            if record.parent_dest_add_id:
                parent_dest_name = record.parent_dest_add_id.partner_id.name
                parent_dest_first = record.parent_dest_add_id.partner_id.firstname
                if parent_dest_first :
                    res[record.id]['parent_dest'] += parent_dest_first + ' '
                if parent_dest_name :
                    res[record.id]['parent_dest'] += parent_dest_name
        return res
    
    _columns = {
        'name' : fields.char('Description', size = 128),
        'type' : fields.selection([
                ('out_certificate','Customer Certificate'),
                ('in_certificate','Supplier Certificate'),
                ],'Type', readonly=True),
        'number' : fields.char('Certificate Number', size = 32, readonly=True, help="Unique number of the certificate, computed automatically when the certificate is validated."),
        'partner_id' : fields.many2one('res.partner', 'Partner', required=True),
        'partner_address_id' : fields.many2one('res.partner', 'Partner address', required=True),
        'salesman_id' : fields.many2one('res.users', 'Salesman'),
#        'amount_untaxed' : fields.function(_get_total, type = 'float', store = True, method=True, string = 'Amount untaxed', multi='all'),
#        'amount_tax' : fields.function(_get_total, type = 'float', store = True, method=True, string = 'Amount tax', multi='all'),
        'amount_untaxed' : fields.float('Amount untaxed'),
        'amount_tax' : fields.float('Amount tax'),
        'amount_total' : fields.float('Amount total'),
        'payment_done' : fields.float('Payment Cesu Done'),
        'currency_id': fields.many2one('res.currency', 'Currency', readonly=True, states={'draft':[('readonly',False)]}),
        'state': fields.selection([
                ('draft','Draft'),
                ('open','Open'),
                ('cancel','Cancelled')
                ],'State', readonly=True),
        'invoice_ids' : fields.many2many('account.invoice', 'account_invoice_certificate_rel', 'invoice_id', 'certificate_id', 'Invoices'),
        'invoice_line_ids': fields.many2many('account.invoice.line', 'account_invoice_line_certificate_rel', 'line_id', 'certificate_id', 'Invoice lines'),
        'date' : fields.date('Date Certificate', states={'open':[('readonly',True)]}, help="Keep empty to use the current date"),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscalyear', readonly=True, required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'line_ids' : fields.one2many('tax.certificate.line', 'certificate_id', 'Tax certificate lines'),
        'notes' : fields.text('Notes'),
        'origin' : fields.char('Origin', size=32),
    }
    
    _defaults = {
        'type': _get_type,
        'state': lambda *a: 'draft',
        'currency_id': _get_currency,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'tax.certificate', context=c),
    }

    def get_number(self, cr, uid, certificate_type, context=None):
        number = self.pool.get('ir.sequence').next_by_code(cr, uid, 'tax.certificate.' + certificate_type)
        return number
    
    def validate_certificate(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        today = DateTime.today()
        datas = {
            'state' : 'open',
            'date' : today,
            'number' : False,
        }
        certificates = self.browse(cr, uid, ids)
        for certificate in certificates:
            state = certificate.state
            if state == 'draft':
                number = self.get_number(cr, uid, certificate.type, context)
                if number:
                    datas['number'] = number
                self.write(cr, uid, [certificate.id], datas, context)
        return ids
    
    def _compute_data(self, cr, uid, certificate_id, context=None):
        if context == None:
            context = {}
        certificate = self.browse(cr, uid, certificate_id, context=context)
        tax_obj = self.pool.get('account.tax')
        total_untaxed = 0
        total_tax = 0
        total = 0
        product_ids = []
        for invoice_line in certificate.invoice_line_ids:
            if invoice_line.invoice_id.reconciled:
                if product_ids and invoice_line.product_id.id in product_ids or not product_ids:
                    total_untaxed += invoice_line.price_subtotal
                    for tax in tax_obj.compute_all(cr, uid, invoice_line.invoice_line_tax_id, (invoice_line.price_unit* (1-(invoice_line.discount or 0.0)/100.0)), invoice_line.quantity, invoice_line.invoice_id.address_invoice_id.id, invoice_line.product_id, invoice_line.invoice_id.partner_id)['taxes']:
                        total_tax += tax['amount']
        total += total_untaxed + total_tax
        vals = {'amount_untaxed': total_untaxed, 'amount_tax': total_tax, 'amount_total': total}
        return vals
    
    def update_amount(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        certificates = self.browse(cr, uid, ids)
        for certificate in certificates:
            vals = self._compute_data(cr, uid, certificate.id, context=context)
            self.write(cr, uid, certificate.id, vals, context=context)
        return True
    
    def create_certificate(self, cr, uid, invoice_ids, fiscalyear, product_ids, context=None):
        if context == None:
            context = {}
        if product_ids == None:
            product_ids = []
        invoice_obj = self.pool.get('account.invoice')
        invoices = invoice_obj.browse(cr, uid, invoice_ids, context)
        today = DateTime.today()
        str_today = str(today).split(' ')[0]
        partner_ids = []
        certificate_ids = []
        for invoice in invoices:
            partner = invoice.partner_id
            if not partner in partner_ids:
                partner_ids.append(partner)
        for partner in partner_ids:
            partner_address_id = False
            if partner.address:
                partner_address_id = partner.address[0].id
            salesman_id = partner.user_id and partner.user_id.id or False
            partner_invoice_ids = []
            for invoice in invoices:
                if invoice.partner_id.id == partner.id :
                    partner_invoice_ids.append(invoice.id)
            domain = [('invoice_id', 'in', partner_invoice_ids)]
            if product_ids:
                domain.append(('product_id', 'in', product_ids))
            partner_invoice_line_ids = self.pool.get('account.invoice.line').search(cr, uid, domain, context=context)
            vals = {
                'name' : str_today + ' - ' + fiscalyear.name + ' - ' + partner.name,
                'partner_id' : partner.id,
                'fiscalyear_id' : fiscalyear.id,
                'partner_address_id' : partner_address_id,
                'invoice_ids' : [(6,0,partner_invoice_ids)],
                'invoice_line_ids' : [(6,0, partner_invoice_line_ids)],
                'salesman_id': salesman_id,
            }
            if partner.company_id:
                vals.update({'company_id': partner.company_id.id})
            certificate_ids.append(self.create(cr, uid, vals, context=context))
        if certificate_ids:
            self.compute_lines(cr, uid, certificate_ids, context=context)
            self.update_amount(cr, uid, certificate_ids, context=context)
        return certificate_ids
    
    def compute_lines(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        certificates = self.browse(cr, uid, ids)
        line_obj = self.pool.get('tax.certificate.line')
#        tax_emp_obj = self.pool.get('tax.certificate.employee')
        for certificate in certificates:
            line_obj.compute_lines(cr, uid, certificate, context=context)
        return True
    
#    def write(self, cr, uid, ids, vals, context=None):
#        super(tax_certificate, self).write(self, cr, uid, ids, vals, context=context)
#        self.compute_lines(cr, uid, ids, context=context)
#        return True
#    
#    def create(self, cr, uid, vals, context=None):
#        new_id = super(tax_certificate, self).create(self, cr, uid, vals, context=context)
#        self.compute_lines(cr, uid, [new_id], context=context)
#        return new_id
    
tax_certificate()

class tax_certificate_line(osv.osv):
    _name = "tax.certificate.line"
    _description ='Tax Certificate lines'

    _columns = {
        'certificate_id': fields.many2one('tax.certificate', 'Certificate', required=True, ondelete='cascade'),
        'period_id': fields.many2one('account.period', 'Period'),
        'analytic_id': fields.many2one('account.analytic.line', 'Account analytic line', required=True),
        'product_id': fields.many2one('product.product', 'Product'),
    }
    
    def compute_lines(self, cr, uid, certificate, context=None):
        if context == None:
            context = {}
        account_analytic_line_obj = self.pool.get('account.analytic.line')
        line_obj = self.pool.get('tax.certificate.line')
        period_obj = self.pool.get('account.period')
        to_del_ids = line_obj.search(cr, uid, [('certificate_id', '=', certificate.id)])
        analytic_account_ids = []
        for x in certificate.invoice_line_ids:
            if x.account_analytic_id.id and x.account_analytic_id.id not in analytic_account_ids:
                analytic_account_ids.append(x.account_analytic_id.id)
        date_start = certificate.fiscalyear_id.date_start
        date_stop = certificate.fiscalyear_id.date_stop
        fiscalyear_id = certificate.fiscalyear_id.id
        analytic_line_ids = account_analytic_line_obj.search(cr, uid, [('account_id', 'in', analytic_account_ids),('date','>=',date_start),('date','<=',date_stop)])
        if analytic_line_ids:
            analytic_lines = account_analytic_line_obj.browse(cr, uid, analytic_line_ids)
            for analytic_line in analytic_lines:
                period_id = False
                if analytic_line.invoice_id and analytic_line.product_id.id not in [1362,1394,1493]:
                    period_id = analytic_line.invoice_id.period_id and analytic_line.invoice_id.period_id.id
                else:
                    date = analytic_line.date
                    period_ids = period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscalyear_id),('date_start','<=',date),('date_stop','>=',date)])
                    if period_ids:
                        period_id = period_ids[0]
                vals = {
                    'certificate_id': certificate.id,
                    'analytic_id': analytic_line.id,
                    'period_id': period_id or False,
                    'product_id': analytic_line.product_id and analytic_line.product_id.id or False,
                }
                line_obj.create(cr, uid, vals)
        line_obj.unlink(cr, uid, to_del_ids)
        return True

tax_certificate_line()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
