# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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
import openerp.addons.decimal_precision as dp

class hr_expense_expense(orm.Model):
    _inherit = 'hr.expense.expense'

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.line_ids:
                total += line.total_amount
            res[expense.id] = total
        return res

    _columns = {
        'amount': fields.function(_amount, string='Total Amount',
            digits_compute=dp.get_precision('Account')),
    }

class hr_expense_line(orm.Model):
    _inherit = 'hr.expense.line'

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = super(hr_expense_line, self).\
            _amount(cr, uid, ids, field_name, arg, context=context)
        
        for record in self.browse(cr, uid, ids, context=context):
            if record.currency_rate and record.currency_rate != 0:
                res[record.id] /= record.currency_rate
        return res

    def _get_currency_rate(self, cr, uid, ids, field_name, arg, context=None):
        """Returns a dictionary with key=the ID of a record
        and value = the level of this  
        record in the tree structure."""
        res = {}
        expense_obj = self.pool.get('hr.expense.expense')
        currency_obj = self.pool.get('res.currency')
        for expense_line in self.browse(cr, uid, ids, context=context):
            currency_rate = 0
            line_currency = expense_line.currency_id or False
            expense_currency = expense_line.expense_id.currency_id or False
            if line_currency:
                if line_currency.id == expense_currency.id:
                    currency_rate = 1
                else:
                    currency_rate = line_currency.rate_silent / expense_currency.rate_silent
            res[expense_line.id] = currency_rate
        return res

    _columns = {
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'currency_rate': fields.function(_get_currency_rate,
            string='Current Rate', digits=(12,6), store=True),
        'total_amount': fields.function(_amount, string='Total',
            digits_compute=dp.get_precision('Account')),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
