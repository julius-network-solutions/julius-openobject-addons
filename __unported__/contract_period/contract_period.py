# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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

import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class res_company(models.Model):
    _inherit = 'res.company'
    quantity_default = fields.Float('Default quantity')

class contract_period(models.Model):
    _name = "contract.period"
    _description = "Contracts period"
    _order = 'date_start, date_end'

    date_start = fields.Date('Date start', required=True)
    date_end = fields.Date('Date end', required=True)
    quantity = fields.Float('Quantity', required=True)
    active = fields.Boolean('Active', default=True)
#     contract_id = fields.Many2one('contract.contract', 'Contract')
    account_id = fields.Many2one('account.analytic.account', 'Contract')
    company_id = fields.Many2one('res.company', 'Company')
    interval_type = fields.Selection([
                                      ('daily', 'Day(s)'),
                                      ('weekly', 'Week(s)'),
                                      ('monthly', 'Month(s)'),
                                      ('yearly', 'Year(s)'),
                                      ], 'Interval type', required=True,
                                     default='months')
    
class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    date_init = fields.Date('First Billing Date')
    invoice_term = fields.Selection([
                                     ('payable_before', 'Payable in advance'),
                                     ('payable_after', 'Payable at the end'),
                                     ], 'Invoice term',
                                    default='payable_before')
    quantity_default_specific = fields.\
        Float('Specific default quantity',
              help="If you don't choose a value here the system " \
              "will get the default company value")
    quantity_default = fields.Float('Default quantity to invoice',
                                    compute='_get_quantity_to_invoice',
                                    store=False)

    @api.one
    def _get_quantity_to_invoice(self):
        self.quantity_default = self.quantity_default_specific or \
            self.company_id.quantity_default or 0

    @api.model
    def _get_search_period_domain(self, contract, date, delta):
        date_end = date + delta
        if date_end > date:
            date_start = date
        else:
            date_start = date_end
            date_end = date
        date_start = datetime.datetime.strftime(date_start, DF)
        date_end = datetime.datetime.strftime(date_end, DF)
        res = [
               ('interval_type', '=', contract.recurring_rule_type),
               ('date_start', '<=', date_start),
               ('date_end', '>=', date_end),
               ]
        return res

    @api.model
    def _get_line_quantity(self, contract, date=False):
        res = 0
        interval_number = contract.recurring_interval or 1
        interval_type = contract.recurring_rule_type
        invoice_term = contract.invoice_term or 'payable_before'
        if not date:
            date = contract.next_invoice_date or contract.date_init or \
                contract.date_start or datetime.datetime.today()
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, DF)
        i = 0
        delta = False
        up_delta = False
        if interval_type == 'yearly':
            month = (invoice_term == 'payable_after' and -1 or 1) * 12
            day = invoice_term == 'payable_after' and 1 or -1
            delta = relativedelta(months=month,days=day)
            up_delta = relativedelta(months=month)
        if interval_type == 'monthly':
            month = invoice_term == 'payable_after' and -1 or 1
            day = invoice_term == 'payable_after' and 1 or -1
            delta = relativedelta(months=month,days=day)
            up_delta = relativedelta(months=month)
        elif interval_type == 'weekly':
            delta = relativedelta(days=invoice_term == 'payable_after' and -6 or 6)
            up_delta = relativedelta(days=invoice_term == 'payable_after' and -7 or 7)
        else:
            delta = relativedelta(days=invoice_term == 'payable_after' and -1 or 1)
            up_delta = relativedelta(days=invoice_term == 'payable_after' and -1 or 1)
        period_obj = self.env['contract.period']
        while i < interval_number:
            if interval_number <= 0:
                break
            i += 1
            domain = self._get_search_period_domain(contract, date, delta)
            domain_without_contract = domain + [('account_id', '=', False)]
            domain_contract = domain + [('account_id', '=', contract.id)]
            if up_delta:
                date = date + up_delta
            periods = period_obj.search(domain_contract)
            if not periods:
                periods = period_obj.search(domain_without_contract)
            if not periods:
                res += contract.quantity_default
                continue
            for period in periods:
                res += period.quantity
        return res

    @api.model
    def _get_invoice_line_vals(self, line, contract,
                               account_id, tax_id, date=False):
        quantity = line.quantity
        if not quantity:
            quantity = self._get_line_quantity(contract, date)
        if self._context.get('force_company') or \
            self._context.get('company_id'):
            company_id = self._context.get('force_company') or \
                self._context.get('company_id')
            tax_id = tax_id.filtered(lambda t: t.company_id.id == company_id)
        return {
                'name': line.name,
                'account_id': account_id,
                'account_analytic_id': contract.id,
                'price_unit': line.price_unit or 0.0,
                'quantity': quantity or 0,
                'uos_id': line.uom_id.id or False,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, tax_id.ids)],
                }

    @api.model
    def _prepare_invoice_lines(self, contract, fiscal_position_id):
        fpos_obj = self.env['account.fiscal.position']
        fiscal_position = fpos_obj
        if fiscal_position_id:
            fiscal_position = fpos_obj.browse(fiscal_position_id)
        invoice_lines = []
        date = self._context.get('date')
        if not date:
            date = contract.recurring_next_date
            if not date:
                date = fields.Date.today()
        for line in contract.recurring_invoice_line_ids:
            res = line.product_id
            account_id = res.property_account_income.id
            if not account_id:
                account_id = res.categ_id.property_account_income_categ.id
            account_id = fiscal_position.map_account(account_id)
            taxes = res.taxes_id
            tax_id = fiscal_position.map_tax(taxes)
            vals = self.with_context(company_id=contract.company_id.id).\
                _get_invoice_line_vals(line, contract,
                                       account_id, tax_id, date)
            invoice_lines.append((0, 0, vals))
        return invoice_lines

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
