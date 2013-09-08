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

from osv import fields, orm
from tools.translate import _

class account_tax(orm.Model):
    _inherit = 'account.tax'
    _columns = {
        'hide': fields.boolean('Hide'),
    }
    _defaults = {
        'hide': lambda *a: False,
    }
    
    def _unit_compute(self, cr, uid, taxes, price_unit, product=None, partner=None, quantity=0):
        res = super(account_tax, self)._unit_compute(cr, uid,  taxes, price_unit, product=product, partner=partner, quantity=quantity)
        for data in res: 
            tax_id = data.get('id')
            hide = self.browse(cr,uid, tax_id).hide
            data.update({'hide': hide})
        return res
    
    def _unit_compute_inv(self, cr, uid, taxes, price_unit, product=None, partner=None):
        res = super(account_tax, self)._unit_compute_inv(cr, uid,  taxes, price_unit, product=product, partner=partner)
        for data in res: 
            tax_id = data.get('id')
            hide = self.browse(cr,uid, tax_id).hide
            data.update({'hide': hide})
        return res


class account_invoice_tax(orm.Model):
    _inherit = 'account.invoice.tax'
    _columns = {
        'hide': fields.boolean('Hide'),
    }
    
    def compute(self, cr, uid, invoice_id, context=None):
        res = super(account_invoice_tax, self).compute(cr, uid, invoice_id, context=context)        
        tax_obj = self.pool.get('account.tax')
        invoice_obj = self.pool.get('account.invoice')
        inv = invoice_obj.browse(cr, uid, invoice_id, context=context)
        for line in inv.invoice_line:
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, inv.partner_id)['taxes']:
                val={}
                if inv.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                res[key].update({'hide': tax['hide']})
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
