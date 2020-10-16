# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, _

def _to_unicode(s):
    try:
        return s.decode('utf-8')
    except UnicodeError:
        try:
            return s.decode('latin')
        except UnicodeError:
            try:
                return s.encode('ascii')
            except UnicodeError:
                return s

class account_move(models.Model):
    _inherit = 'account.move'
    
    _columns = {}
    
    def _groupLines(self, cr, uid, ids, lines, credit=False, debit=False, context=None):
        line_obj = self.pool.get('account.move.line')
        for line in lines:
            account_id = line[0]
            reconcile_id = line[1]
            reconcile_partial_id = line[2]
            statement_id = line[3]
            currency_id = line[4]
            period_id = line[5]
            move_id = line[6]
            analytic_account_id = line[7]
            journal_id = line[8]
            tax_code_id = line[9]
            partner_id = line[10]
            amount_taxed = line[11] or 0.0
            amount_currency = line[12] or 0.0
            tax_amount = line[13] or 0.0
            credit = line[14] or 0.0
            debit = line[15] or 0.0
            date = line[16]
            ref = line[17]
            state = line[18]
            company_id = line[19]
            domain = [('move_id', '=', move_id),]
            request_columns = '(move_id, amount_taxed, amount_currency, tax_amount, credit, debit, date, ref'
            request_data = [move_id, amount_taxed or 0, amount_currency or 0, tax_amount or 0, credit, debit, date, str(ref)]
            if account_id:
                domain.append(('account_id', '=', account_id),)
                request_columns += ', account_id'
                request_data.append(account_id)
            else:
                domain.append(('account_id', '=', None),)
            if reconcile_id:
                domain.append(('reconcile_id', '=', reconcile_id),)
                request_columns += ', reconcile_id'
                request_data.append(reconcile_id)
            else:
                domain.append(('reconcile_id', '=', None),)
            if reconcile_partial_id:
                domain.append(('reconcile_partial_id', '=', reconcile_partial_id),)
                request_columns += ', reconcile_partial_id'
                request_data.append(reconcile_partial_id)
            else:
                domain.append(('reconcile_partial_id', '=', None),)
            if statement_id:
                domain.append(('statement_id', '=', statement_id),)
                request_columns += ', statement_id'
                request_data.append(statement_id)
            else:
                domain.append(('statement_id', '=', None),)
            if currency_id:
                domain.append(('currency_id', '=', currency_id),)
                request_columns += ', currency_id'
                request_data.append(currency_id)
            else:
                 domain.append(('currency_id', '=', None),)
            if period_id:
                domain.append(('period_id', '=', period_id),)
                request_columns += ', period_id'
                request_data.append(period_id)
            else:
                domain.append(('period_id', '=', None),)
            if analytic_account_id:
                domain.append(('analytic_account_id', '=', analytic_account_id),)
                request_columns += ', analytic_account_id'
                request_data.append(analytic_account_id)
            else:
                domain.append(('analytic_account_id', '=', None),)
            if journal_id:
                domain.append(('journal_id', '=', journal_id),)
                request_columns += ', journal_id'
                request_data.append(journal_id)
            else:
                domain.append(('journal_id', '=', None),)
            if tax_code_id:
                domain.append(('tax_code_id', '=', tax_code_id),)
                request_columns += ', tax_code_id'
                request_data.append(tax_code_id)      
            else:
                domain.append(('tax_code_id', '=', None),)
            if partner_id:
                domain.append(('partner_id', '=', partner_id),)
                request_columns += ', partner_id'
                request_data.append(partner_id)
            else:
                domain.append(('partner_id', '=', None),)
            if state:
                domain.append(('state', '=', str(state)),)
                request_columns += ', state'
                request_data.append(str(state))
            else:
                domain.append(('state', '=', None),)
            if debit:
                domain.append(('debit', '>=', 0.01),)
            elif credit:
                domain.append(('credit', '>=', 0.01),)
            if company_id:
                domain.append(('company_id', '=', company_id),)
                request_columns += ', company_id'
                request_data.append(company_id)
            else:
                domain.append(('company_id', '=', None),)
            line_ids = line_obj.search(cr, uid, domain)
            if line_ids and len(line_ids) > 1:
                name = ''
                for line in line_ids:
                    line_name = line_obj.browse(cr, uid, line).name
                    name = name and name + ', ' + line_name or line_name
                request_columns += ', name)'
                name = str(name).replace("'",' ')
                name = name[:64]
                request_data.append(name)
                str_request_data = '('
                first = True
                for val in request_data:
                    if not first:
                        str_request_data += ','
                    else:
                        first = False
                    if isinstance(val,str):
                        str_request_data += "'"
                    str_request_data += str(val)[:64]
                    if isinstance(val,str):
                        str_request_data += "'"
                str_request_data += ')'
                str_request_data = _to_unicode(str_request_data.replace('"',"'"))
                cr.execute("""DELETE FROM account_move_line WHERE id in %s """ %(str(tuple(line_ids))))
                cr.execute("""INSERT INTO account_move_line %s VALUES %s """ %(request_columns, str_request_data))
        return True
    
    def action_group_lines(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        for move in self.browse(cr, uid, ids):
            cr.execute("""SELECT account_id, reconcile_id, reconcile_partial_id, statement_id, currency_id, period_id, move_id, analytic_account_id, journal_id, tax_code_id, partner_id,
                                 sum(amount_taxed), sum(amount_currency), sum(tax_amount), sum(credit), sum(debit), date, ref, state, company_id
                            FROM account_move_line
                            WHERE id in (SELECT id FROM account_move_line WHERE credit >= 0.01 AND (debit < 0.01 OR debit IS NULL ) AND move_id = %s )
                            GROUP BY account_id, reconcile_id, reconcile_partial_id, statement_id, currency_id, period_id, move_id, analytic_account_id, journal_id, tax_code_id, partner_id, date, ref, state, company_id 
                            ORDER BY move_id """ %(move.id))
            credit_lines = cr.fetchall()
            self._groupLines(cr, uid, ids, credit_lines, True, False, context)
            cr.execute("""SELECT account_id, reconcile_id, reconcile_partial_id, statement_id, currency_id, period_id, move_id, analytic_account_id, journal_id, tax_code_id, partner_id,
                                 sum(amount_taxed),sum(amount_currency),sum(tax_amount),sum(credit),sum(debit), date, ref, state, company_id
                            FROM account_move_line
                            WHERE id in (SELECT id FROM account_move_line WHERE debit >= 0.01 AND (credit < 0.01 OR credit IS NULL)  AND move_id = %s )
                            GROUP BY account_id, reconcile_id, reconcile_partial_id, statement_id, currency_id, period_id, move_id, analytic_account_id, journal_id, tax_code_id, partner_id, date, ref, state, company_id
                            ORDER BY move_id """ %(move.id))
            debit_lines = cr.fetchall()
            self._groupLines(cr, uid, ids, debit_lines, False, True, context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
