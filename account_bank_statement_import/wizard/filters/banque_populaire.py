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

from . import conversion

def get_data(self, recordlist, data):
    account_period_obj = self.env['account.period']
    bank_statement_obj = self.env['account.bank.statement']
    line_obj = self.env['account.bank.statement.line']
    bank_statements = []
    pointor = 0        
    total_amount = 0
    bank_statement = {}
    bank_statement_lines = {}
    bank_statement["bank_statement_line"] = {}
    date_format = data.get('date_format')
    # Loop on all line of a month
    for line in recordlist[1:]:
        line_splited = line.split(';') 
        st_line = {}
        line_name = pointor
        st_line['extra_note'] = ''
        st_line['name'] = line_splited[3]
        st_line['ref'] = line_splited[4]
        st_line['date'] = line_splited[5]
        amount = line_splited[6]
        '''Definition of a positive or negative value'''
        if amount.startswith('-'):
            st_line['account_id'] = data['payable_id']
        else:
            st_line['account_id'] = data['receivable_id']
        amount = float(amount or 0.0)
        st_line['amount'] = amount
        st_line['partner_id'] = False
        # check of uniqueness of a field in the data base            
        check_ids = line_obj.search([
                                     ('name', '=', line_splited[1]),
                                     ('date', '=', line_splited[2]),
                                     ('amount', '=', amount)
                                     ])
        if check_ids:
            continue        
        if not check_ids:   
            bank_statement_lines[line_name] = st_line
        bank_statement["bank_statement_line"] = bank_statement_lines
        pointor += 1
        total_amount += amount
    # Saving data at month level
    bank_statement["total_amount"] = total_amount
    date = conversion.str2date(st_line['date'], date_format)
    period_id = account_period_obj.search([
                                           ('date_start', '<=', date),
                                           ('date_stop', '>=', date),
                                           ], limit=1)
    bank_statement['date'] = date
    bank_statement['period_id'] = period_id and period_id[0] or False
    bank_statements.append(bank_statement)
    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
