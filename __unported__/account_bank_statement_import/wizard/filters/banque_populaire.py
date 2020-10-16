# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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
#
# This filter imports .coda-files (CODA-layout).
#

import time
from . import conversion


def get_data(self, recordlist):
    
    account_period_obj = self.env['account.period']
    bank_statement_obj = self.env['account.bank.statement']
    journal_obj = self.env['account.journal']
    journal_code = journal_obj.code
    
    bank_statements = []
    i = 0        
    first_line = True    
#    month_statement = {}
#    month_statement_period = {}
    
    # first loop on each line to determine the number of month in the statement
#    for line_1 in recordlist:
#        line_splited_1 = line_1.split('\t') 
#        if first_line:
#            first_line = False
#            continue
#               
#        st_line_1 = {}
#        st_line_1['date'] = line_splited_1[5].replace('"','')
#        
#        line_period = time.strftime('%Y-%m', time.strptime(st_line_1['date'], "%d/%m/%Y"))
#       
#        if line_period in month_statement.keys():
#            month_statement[line_period].append(line_1)
#        else:
#            month_statement[line_period] = [line_1]
#            month_statement_period[line_period] = line_period
        
    # loop on each month        
#    for key in month_statement.keys():
               
    total_amount = 0
    bank_statement = {}
    bank_statement_lines = {}
    bank_statement["bank_statement_line"] = {}

    # Loop on all line of a month
    for line in recordlist:
        if first_line:
            first_line = False
            continue

        line_splited = line.split(';') 
        st_line = {}
        line_name = i
        st_line['extra_note'] = ''
        st_line['name'] = line_splited[3]
        st_line['ref'] = line_splited[4]
        st_line['date'] = line_splited[5]
        amount = line_splited[6]
        
        '''Definition of a positive or negative value'''
        if amount.startswith('-'):
            st_line['account_id'] = self.payable_id.id
        else:
            st_line['account_id'] = self.receivable_id.id
        
        # Format conversion
        if '.' in amount:
            amount = amount.replace('.', '')
        if ' ' in amount:
            amount = amount.replace(' ', '')
        if ',' in amount:
            amount = amount.replace(',', '.')

        amount = float(amount or 0.0)
        st_line['amount'] = amount
        st_line['partner_id'] = False
        
        # check of uniqueness of a field in the data base            
        check_ids = self.env['account.bank.statement.line'].search([('name', '=', line_splited[1]), ('date', '=', line_splited[2]), ('amount', '=', amount)])
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
    bank_statement['journal_id'] = self.journal_id.id
    period_id = account_period_obj.search([('date_start', '<=', time.strftime('%Y-%m-%d', time.strptime(st_line['date'], "%d/%m/%Y"))), ('date_stop', '>=', time.strftime('%Y-%m-%d', time.strptime(st_line['date'], "%d/%m/%Y")))])
    bank_statement['date'] = time.strftime('%Y/%m/%d', time.strptime(st_line['date'], "%d/%m/%Y"))
    bank_statement['period_id'] = period_id and period_id[0] or False
    bank_statements.append(bank_statement)

    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
