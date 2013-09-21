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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class account_journal(orm.Model):
    _inherit = 'account.journal'

    _columns = {
        'sequence_name2_id': fields.many2one('ir.sequence', 'Name2 Sequence',
            help="This field contains the information related "
            "to the numbering of the invoices of this journal."),
    }

    def copy(self, cr, uid, id, default=None,
             context=None, done_list=None, local=False):
        default = {} if default is None else default.copy()
        default.update(
            sequence_name2_id=False)
        return super(account_journal,
            self).copy(cr, uid, id, default, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        for journal in self.browse(cr, uid, ids, context=context):
            sequence_vals = {}
            if not journal.sequence_name2_id:
                sequence_vals['name'] = (vals.get('name') or \
                    journal.name) + _(' Invoice name')
                sequence_vals['code'] = vals.get('code') or journal.code
                vals.update({
                    'sequence_name2_id': self.create_sequence(
                        cr, SUPERUSER_ID, sequence_vals, context)
                    })
        return super(account_journal,
            self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        if not 'sequence_name2_id' in vals or not vals['sequence_name2_id']:
            # if we have the right to create a journal, we should be able to
            # create it's sequence.
            vals.update({
                'sequence_name2_id': self.create_sequence(
                    cr, SUPERUSER_ID, vals, context)
                    })
        return super(account_journal, self).create(cr, uid, vals, context)

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'name2': fields.char('Name 2'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        default = default or {}
        default.update({
            'name2': False,
        })
        return super(account_invoice,
            self).copy(cr, uid, id, default=default, context=context)

    def action_number(self, cr, uid, ids, context=None):
        res = super(account_invoice,
            self).action_number(cr, uid, ids, context=context)
        obj_sequence = self.pool.get('ir.sequence')
        for invoice in self.browse(cr, uid, ids, context=context):
            if not invoice.name2:
                if invoice.journal_id.sequence_name2_id:
                    c = {'fiscalyear_id': invoice.period_id.fiscalyear_id.id}
                    name2 = obj_sequence.next_by_id(
                        cr, uid, invoice.journal_id.sequence_name2_id.id, c)
                else:
                    raise orm.except_orm(_('Error!'),
                                         _('Please define a sequence '
                                           'on the journal for the name '
                                           'of the invoice.'))
                if name2:
                    self.write(cr, uid, [invoice.id], {
                        'name2': name2
                        }, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: