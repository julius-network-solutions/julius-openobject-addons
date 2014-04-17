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

class hr_expense_expense(orm.Model):
    _inherit = "hr.expense.expense"

    def move_line_get(self, cr, uid, expense_id, context=None):
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        exp = self.browse(cr, uid, expense_id, context=context)
        company_currency = exp.company_id.currency_id.id

        for line in exp.line_ids:
            mres = self.move_line_get_item(cr, uid, line, context)
            if not mres:
                continue
            res.append(mres)
            tax_code_found= False
            
            #Calculate tax according to default tax on product
            taxes = []
            #Taken from product_id_onchange in account.invoice
            if line.product_id:
                fposition_id = False
                fpos_obj = self.pool.get('account.fiscal.position')
                fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
                product = line.product_id
                taxes = product.supplier_taxes_id
                #If taxes are not related to the product, maybe they are in the account
                if not taxes:
                    a = product.property_account_expense.id #Why is not there a check here?
                    if not a:
                        a = product.categ_id.property_account_expense_categ.id
                    a = fpos_obj.map_account(cr, uid, fpos, a)
                    taxes = a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False
                tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
            if not taxes:
                continue
            #Calculating tax on the line and creating move?
            for tax in tax_obj.compute_all(cr, uid, taxes,
                    line.unit_amount ,
                    line.unit_quantity, line.product_id,
                    exp.user_id.partner_id)['taxes']:
                tax_code_id = tax['base_code_id']
                tax_amount = line.total_amount * tax['base_sign']
                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(cr, uid, line, context))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True
                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = cur_obj.compute(cr, uid, exp.currency_id.id, company_currency, tax_amount, context={'date': exp.date_confirm})
                ## 
                is_price_include = tax_obj.read(cr,uid,tax['id'],['price_include'],context)['price_include']
                if is_price_include:
                    ## We need to deduce the price for the tax
                    res[-1]['price'] = res[-1]['price'] - (tax['amount'] * -tax['base_sign'] or 0.0)
                    res[-1]['tax_amount'] = res[-1]['tax_amount'] - (tax['amount'] * tax['base_sign'] or 0.0)
                assoc_tax = {
                             'type':'tax',
                             'name':tax['name'],
                             'price_unit': tax['price_unit'],
                             'quantity': 1,
                             'price':  -tax['amount'] * tax['base_sign'] or 0.0,
                             'account_id': tax['account_collected_id'] or mres['account_id'],
                             'tax_code_id': tax['tax_code_id'],
                             'tax_amount': tax['amount'] * tax['base_sign'],
                             }
                res.append(assoc_tax)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
