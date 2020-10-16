# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT)
from datetime import datetime, timedelta

class one2many_mod(fields.one2many):
    
    def get(self, cr, obj, ids, name, user=None,
            offset=0, context=None, values=None):
        if context is None:
            context = {}
        if self._context:
            context = context.copy()
        context.update(self._context)
        context.update({
                'default_active': False,
                'active_test': False,
            })
        return super(one2many_mod, self).\
            get(cr, obj, ids, name, user=user,
                offset=offset, context=context, values=values)

class period_contract(orm.Model):
    _name = 'period.contract'
    _description = "Contract Period"
    _columns = {
        'name': fields.char('Name', size=64),
        'from_dt': fields.date('From date'),
        'to_dt': fields.date('To date'),
        'guaranteed': fields.boolean('Guaranteed'),
        'contract_id': fields.many2one('account.analytic.account','Contract')
    }

class account_analytic_account(orm.Model):
    _inherit = 'account.analytic.account'
    _columns = {
        'active': fields.boolean('Active'),
        'client_num': fields.char('Client Number', size=64),
        'period_ids': fields.one2many('period.contract', 'contract_id',
                                      'Periods'),
        'invoice_ids': fields.one2many('account.invoice', 'contract_id',
                                       'Invoices', readonly=True),
        'product_ids': one2many_mod('product.product', 'contract_id',
                                    'Products'),
        'sap_number': fields.char('SAP Number', size=64),
        'payment_term_id': fields.many2one('account.payment.term',
                                           'Payment Term'),
    }
    
    _defaults = {
        'code': lambda self, cr, uid, context: self.pool.get('ir.sequence').\
            next_by_code(cr, uid, 'account.analytic.contract'),
        'active': True,
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('type') == 'contract':
            if not vals.get('period_ids'):
                raise orm.except_orm(_('Error'),
                                     _("Please specify at least one period !"))
        res = super(account_analytic_account, self).\
            create(cr, uid, vals, context=context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        for contract in self.browse(cr, uid, ids, context=context):
            is_contract = False
            if contract.type == 'contract':
                is_contract = True
            if is_contract:
                period = contract.period_ids
                period_vals = vals.get('period_ids') and \
                    vals['period_ids'][0] \
                    and vals['period_ids'][0][2] or False
                if period_vals:
                    period = period_vals
                if not period:
                    raise orm.except_orm(_('Error'),
                                         _("Please specify at "
                                           "least one period !"))
        return super(account_analytic_account, self).\
            write(cr, uid, ids, vals, context=context)

class account_invoice(orm.Model):
    _inherit = 'account.invoice'
    _columns = {
        'contract_id': fields.many2one('account.analytic.account', 'Contract'),
    }
    
    def onchange_contract_id(self, cr, uid, ids,
                             contract_id=False, context=None):
        vals = {}
        contract_obj = self.pool.get('account.analytic.account')
        if contract_id:
            contract = contract_obj.\
                browse(cr, uid, contract_id, context=context)
            vals = {
                'partner_id': contract.partner_id.id or False,
                'payment_term': contract.payment_term_id.id or False,
            }
        else:
            vals = {
                'partner_id': False,
                'payment_term': False,
            }
        return {'value': vals}
    
class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    def default_get(self, cr, uid, fields, context=None):
        res = super(account_invoice_line, self).\
            default_get(cr, uid, fields, context=context)
        account_invoice_obj = self.pool.get('account.invoice')
        if context is None:
            context={}
        active_id = context.get('active_id')
        if active_id:
            invoice = account_invoice_obj.\
                browse(cr, uid, active_id, context=context)
            contract_id = invoice.contract_id and \
                invoice.contract_id.id or False
            res.update({'account_analytic_id': contract_id})
        return res
    
class product_product(orm.Model):
    _inherit = 'product.product'
    _columns = {
        'contract_id': fields.many2one('account.analytic.account', 'Contract'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
