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

from openerp.osv import fields, orm
from openerp import netsvc
from openerp.tools.translate import _

class sale_order(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'block_without_payment': fields.boolean(
            'Block order Without Payment', readonly=True,
            states={
                    'draft': [('readonly', False)],
                    'sent': [('readonly', False)],
                    }),
        'marked_as_paid': fields.boolean('Marked as Paid',
                                         readonly=True),
    }
    
    _defaults = {
        'block_without_payment': False,
        'marked_as_paid': False,
    }

    def set_marked_as_paid(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.write(cr, uid, ids, {
            'marked_as_paid': True,
            }, context=context)

    def set_marked_as_unpaid(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.write(cr, uid, ids, {
            'marked_as_paid': False,
            }, context=context)
    
    def onchange_payment_term(self, cr, uid, ids,
                              payment_term, context=None):
        if context is None:
            context = {}
        res = {'value': {'block_without_payment': False}}
        if payment_term:
            term_obj = self.pool.get('account.payment.term')
            payment = term_obj.read(cr, uid, payment_term,
                                    ['block_without_payment'],
                                    context=context)
            if payment.get('block_without_payment'):
                val = payment['block_without_payment']
                res['value']['block_without_payment'] = val
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
