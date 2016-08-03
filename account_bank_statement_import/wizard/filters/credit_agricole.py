# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Julius Network Solutions SARL <contact@julius.fr>
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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import base64
import re
from datetime import datetime

def get_data(self, recordlist):

    account_period_obj = self.env['account.period']
    bank_statements = []
    pointor = 0
    line_cursor = 0
    initial_lines = 10
    total_amount = 0
    bank_statement = {}
    bank_statement_lines = {}
    bank_statement["bank_statement_line"] = {}
    
#     obj = self.env['account.bank.statement.import']
#     data = obj.read(ids[0])
#     file_data = recordlist
# 
#     list = base64.decodestring(unicode(file_data, 'utf-8'))
#     list = re.split('\n' + '(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))', list)
    
    list_2 = []
    for l in recordlist:
        if "\n" in l:
            a = l.replace("\n", "")
            list_2.append(a)
        else:
            list_2.append(l)
    
    date_format = self.date_format
    
    for line in list_2:
        if line_cursor < initial_lines:
            line_cursor += 1
            continue
        line_splited = line.split(';') 
        if not line_splited[0]:
            continue
        st_line = {}
        line_name = pointor
        st_line['extra_note'] = ''
        st_line['ref'] = line_splited[2].strip('"')  # Enlever les quotes -> "
        st_line['date'] = time.strftime('%Y-%m-%d', time.strptime(line_splited[0], date_format))
        st_line['name'] = line_splited[2].strip('"')  # Enlever les quotes -> "

        print line_splited

        debit = line_splited[3]
        credit = line_splited[4]

        if debit:
            st_line['account_id'] = self.payable_id.id
            amount = debit
        elif credit:
            st_line['account_id'] = self.receivable_id.id
            amount = credit
        # Format conversion
        if '.' in amount:
            amount = amount.replace('.', '')
        if ' ' in amount:
            amount = amount.replace(' ', '')
        if ',' in amount:
            amount = amount.replace(',', '.')

        amount = float(amount or 0.0)

        if debit:
            amount = -amount

        st_line['amount'] = amount
        st_line['partner_id'] = False



        # check of uniqueness of a field in the data base  
        date = st_line['date']          
        check_ids = self.env['account.bank.statement.line'].search([('ref', '=', line_splited[2]),
                                                                                ('name', '=', line_splited[2]),
                                                                                ('date', '=', date),
                                                                                ('amount', '=', amount)])
        if check_ids:
            continue        
        if not check_ids:   
            bank_statement_lines[line_name] = st_line
            line_name += 1                    
        bank_statement["bank_statement_line"] = bank_statement_lines
        pointor += 1
        total_amount += amount
    # Saving data at month level
    bank_statement['total_amount'] = total_amount
    bank_statement['journal_id'] = self.journal_id.id
    period_id = account_period_obj.search([('date_start', '<=', date), ('date_stop', '>=', date)])
    bank_statement['date'] = date
    bank_statement['period_id'] = period_id and period_id[0] or False
    bank_statements.append(bank_statement)

    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
