# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class payment_order(models.Model):
    _inherit = 'payment.order'

    move_id = fields.Many2one('account.move', 'Move')
    journal_id = fields.Many2one('account.journal', 'Journal')

    @api.one
    def create_account_move(self):
        """
        This method is creating an account move from the payment.
        """
        if not self.journal_id:
            raise Warning(_('Impossible to create the move,'\
                            '\nPlease select a journal.'))
        if self.move_id:
            raise Warning(_("There's already a move related to this payment."))
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        if not self.move_id and self.line_ids:
            today = fields.Date.today()
            move = move_obj.create({
                                    'journal_id': self.journal_id.id,
                                    'company_id': self.company_id.id,
                                    'date': today,
                                    'ref': self.reference,
                                    })
            self.move_id = move.id
        reconciles = []
        group_lines = self.journal_id.group_payment_line
        debit_grouped = 0.0
        credit_grouped = 0.0
        credit_account_id = self.journal_id.default_credit_account_id.id
        debit_account_id = self.journal_id.default_debit_account_id.id
        for line in self.line_ids:
            move_line = line.move_line_id
            if not move_line:
                raise Warning(_('The line %s has not related move' %line.name))
            debit = move_line.debit
            credit = move_line.credit
            account_id = move_line.account_id.id
            if not account_id:
                if debit:
                    account_id = credit_account_id
                else:
                    account_id = debit_account_id
            if not account_id:
                raise Warning(_("There is at least one line without an " \
                                "account defined, so make sure the defaults " \
                                "credit and debit account are defined in " \
                                "the related Journal."))
            to_reconcile_line = move_line_obj.\
                create({
                        'partner_id': move_line.partner_id.id,
                        'name': move_line.name,
                        'journal_id': self.journal_id.id,
                        'date': self.move_id.date,
                        'debit': credit,
                        'credit': debit,
                        'account_id': account_id,
                        'period_id': self.move_id.period_id.id,
                        'move_id': self.move_id.id,
                        })
            if not group_lines:
                other_line = move_line_obj.\
                    create({
                            'partner_id': move_line.partner_id.id,
                            'name': move_line.name,
                            'journal_id': self.journal_id.id,
                            'date': self.move_id.date,
                            'debit': debit,
                            'credit': credit,
                            'account_id': debit and credit_account_id or \
                                debit_account_id,
                            'period_id': self.move_id.period_id.id,
                            'move_id': self.move_id.id,
                            })
            else:
                credit_grouped += credit
                debit_grouped += debit
            reconciles.append(move_line + to_reconcile_line)
        if credit_grouped:
            move_line_obj.\
                create({
                        'partner_id': False,
                        'name': _('Centralized credit'),
                        'journal_id': self.journal_id.id,
                        'date': self.move_id.date,
                        'debit': 0,
                        'credit': credit_grouped,
                        'account_id': debit_account_id,
                        'period_id': self.move_id.period_id.id,
                        'move_id': self.move_id.id,
                        })
        if debit_grouped:
            move_line_obj.\
                create({
                        'partner_id': False,
                        'name': _('Centralized debit'),
                        'journal_id': self.journal_id.id,
                        'date': self.move_id.date,
                        'debit': debit_grouped,
                        'credit': 0,
                        'account_id': credit_account_id,
                        'period_id': self.move_id.period_id.id,
                        'move_id': self.move_id.id,
                        })
        for rec in reconciles:
            rec.reconcile('manual')
        return True

    @api.one
    def delete_account_move(self):
        if not self.move_id:
            raise Warning(_("There's nothing to delete"))
        if self.move_id.state != 'draft':
            raise Warning(_("Impossible to delete this move, " \
                            "please set it to draft before deleting it"))
        line_obj = self.env['account.move.line']
        lines = line_obj.search(['|',
                                 ('reconcile_partial_id', '!=', False),
                                 ('reconcile_id', '!=', False),
                                 ('move_id', '=', self.move_id.id),
                                 ])
        reconciles = self.env['account.move.reconcile']
        for line in lines:
            if line.reconcile_id:
                reconciles |= line.reconcile_id
            if line.reconcile_partial_id:
                reconciles |= line.reconcile_partial_id
        reconciles.unlink()
        self.move_id.unlink()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
