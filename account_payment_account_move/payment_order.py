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

from openerp import models, fields, api

class payment_order(models.Model):
    _inherit = 'payment.order'

    move_id = fields.Many2one('account.move', 'Move')
    journal_id = fields.Many2one('account.journal', 'Journal')

    @api.one
    def create_account_move(self):
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        if not self.move_id:
            today = fields.Date.today()
            move = move_obj.create({
                                    'journal_id': self.journal_id.id,
                                    'company_id': self.company_id.id,
                                    'date': today,
                                    'ref': self.reference,
                                    })
            self.move_id = move.id
        reconciles = []
        for line in self.line_ids:
            move_line = line.move_line_id
            debit_line = move_line_obj.\
                create({
                        'partner_id': move_line.partner_id.id,
                        'name': move_line.name,
                        'journal_id': self.journal_id.id,
                        'date': self.move_id.date,
                        'debit': move_line.credit,
                        'credit': 0,
                        'account_id': move_line.account_id.id,
                        'period_id': self.move_id.period_id.id,
                        'move_id': self.move_id.id,
                        })
            credit_line = move_line_obj.\
                create({
                        'partner_id': move_line.partner_id.id,
                        'name': move_line.name,
                        'journal_id': self.journal_id.id,
                        'date': self.move_id.date,
                        'debit': 0,
                        'credit': move_line.credit,
                        'account_id': self.journal_id.\
                            default_debit_account_id.id,
                        'period_id': self.move_id.period_id.id,
                        'move_id': self.move_id.id,
                        })
            reconciles.append(move_line + debit_line)
        for rec in reconciles:
            rec.reconcile('manual')
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
