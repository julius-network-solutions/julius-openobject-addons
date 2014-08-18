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

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from . import conversion
import time

def get_data(self, cr, uid, ids, recordlist, data):
    
    account_period_obj = self.pool.get('account.period')
    bank_statement_obj = self.pool.get('account.bank.statement')
    line_obj = self.pool.get('account.bank.statement.line')
    
    bank_statements = []
    i = 0        
    month_statement = {}
    
    date_format = data.get('date_format') or '%d/%m/%Y'
    
    # first loop on each line to determine the number of month in the statement
    if len(recordlist) > 5:
        for line_1 in recordlist[5:]:
            line_splited_1 = line_1.split('\t')
            date = line_splited_1[0]
            line_period = time.strftime('%Y-%m',
                                        time.strptime(date, date_format))
            if line_period not in month_statement.keys():
                month_statement[line_period] = []
            month_statement[line_period].append(line_1)
    # loop on each month
    for key in month_statement.keys():
        total_amount = 0
        bank_statement = {}
        bank_statement_lines = {}
        bank_statement["bank_statement_line"] = {}
         # Loop on all line of a month
        for line in month_statement[key]:
            line_splited = line.split('\t') 
            st_line = {}
            line_name = i
            name = line_splited[2]
            st_line['name'] = name
            line_date = line_splited[0]
            st_line['date'] = line_date
            st_line['extra_note'] = ''
            st_line['ref'] = ''
            amount = line_splited[3]
            if amount:
                st_line['account_id'] = data['receivable_id'][0]
                amount = conversion.str2float(amount, ',') or 0.0
            else:
                amount = line_splited[4]
                st_line['account_id'] = data['payable_id'][0]
                amount = - conversion.str2float(amount, ',') or 0.0
            st_line['amount'] = amount
            st_line['partner_id'] = False
            # check of uniqueness of a field in the data base            
            check_ids = line_obj.search(cr, uid, [
                    ('name', '=', name),
                    ('date', '=', line_date),
                    ('amount', '=', amount),
                ])
            if check_ids:
                continue
            if not check_ids:   
                bank_statement_lines[line_name] = st_line
                line_name += 1
            bank_statement["bank_statement_line"] = bank_statement_lines
            i += 1
            total_amount += amount
        # Saving data at month level
        bank_statement["total_amount"] = total_amount
        bank_statement['journal_id'] = data['journal_id'][0]
        bank_statement['date'] = time.strftime('01/%m/%Y',
                                               time.strptime(key,"%Y-%m"))
        date_formated = time.strftime(DEFAULT_SERVER_DATE_FORMAT,
                                      time.strptime(bank_statement['date'],
                                                    date_format))
        period_id = account_period_obj.search(cr, uid, [
                ('date_start', '<=', date_formated),
                ('date_stop', '>=', date_formated)
            ], limit=1)
        bank_statement['period_id'] = period_id and period_id[0] or False
        bank_statements.append(bank_statement)
    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
