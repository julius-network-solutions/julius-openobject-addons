# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _

class account_invoice(orm.Model):
    
    _inherit = 'account.invoice'

    _columns = {
        'origin_invoice_id': fields.many2one('account.invoice', 'Origin invoice',
            domain=[
                ('type', 'in', ('in_invoice', 'out_invoice')),
                ('state', 'not in', ('draft', 'cancel'))
            ], readonly=True, states={'draft':[('readonly',False)]}),
    }

    def _prepare_refund(self, cr, uid, invoice,
                        date=None, period_id=None,
                        description=None, journal_id=None,
                        context=None):
        res = super(account_invoice, self)._prepare_refund(cr, uid, invoice,
                        date=date, period_id=period_id,
                        description=description, journal_id=journal_id,
                        context=context)
        res['origin_invoice_id'] = invoice.id
        origin = ''
        if res.get('origin'):
            origin = res.get('origin')
        res['origin'] = invoice.number + (origin and ':' + origin or '')
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
