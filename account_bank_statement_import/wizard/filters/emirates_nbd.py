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


from osv import fields, osv
import time
import conversion

def get_data(self, cr, uid, ids, recordlist, data):
    
    account_period_obj = self.pool.get('account.period')
    bank_statement_obj = self.pool.get('account.bank.statement')
    journal_obj = self.pool.get('account.journal')
    journal_code = journal_obj.browse(cr, uid, data['journal_id']).code
    
    bank_statements = []
    i = 0
    first_line = True
    month_statement = {}
    date_format = str(self.pool.get('account.bank.statement.import').browse(cr, uid, ids[0]).date_format)
    
    # first loop on each line to determine the number of month in the statement
    for line_1 in recordlist:
        if first_line:
            first_line = False
            continue
        
        line_splited_1 = line_1.split(',')
        if line_splited_1:
            date_value = line_splited_1[1].replace('"','')
#            if date_format == '%d-%b-%y':
#                date_value = date_value[0:6] + '.' + date_value[6:9]
            line_period = time.strftime('%Y-%m',time.strptime(date_value, date_format))
            if line_period in month_statement.keys():
                month_statement[line_period].append(line_1)
            else:
                month_statement[line_period] = [line_1]

    # loop on each month
    for key in month_statement.keys():
               
        total_amount = 0
        bank_statement = {}
        bank_statement_lines = {}
        bank_statement["bank_statement_line"] = {}
        
         # Loop on all line of a month
        for line in month_statement[key]:
            line_splited = line.split(',')
            st_line = {}
            line_name = i
            st_line['extra_note'] = ''
            st_line['ref'] = ''
            st_line['date'] = line_splited[1].replace('"','')
            if date_format == '%d-%b-%y':
#                st_line['date'] = st_line['date'][0:6] + '.' + st_line['date'][6:9]
                st_line['date'] = time.strftime('%Y-%m-%d', time.strptime(st_line['date'], date_format))
            st_line['name'] = line_splited[2].replace('"','') + ' / ' + line_splited[3].replace('"','') + ' / ' + line_splited[4].replace('"','')
            '''Definition of a positive or negative value'''
            if line_splited[5]:
                amount = line_splited[5].replace('"','')
                st_line['account_id'] = data['payable_id'][0]
            elif line_splited[6]:
                amount = line_splited[6].replace('"','')
                st_line['account_id'] = data['receivable_id'][0]    
            amount = float(amount or 0.0)
            st_line['amount'] = amount
            st_line['partner_id'] = False
            
            # check of uniqueness of a field in the data base            
            check_ids = self.pool.get('account.bank.statement.line').search(cr,uid,[('name','=',st_line['name']),('date','=',st_line['date']),('amount','=',st_line['amount'])])
            if check_ids:
                continue
            
            if not check_ids:   
                bank_statement_lines[line_name]=st_line
                line_name += 1
                        
            bank_statement["bank_statement_line"] = bank_statement_lines
            i += 1
            total_amount += amount
            
        # Saving data at month level
        bank_statement["total_amount"] = total_amount
        bank_statement['journal_id'] = data['journal_id'][0]
        bank_statement['date'] = time.strftime('%Y/%m/01', time.strptime(key,"%Y-%m"))
        period_id = account_period_obj.search(cr, uid, [('date_start', '<=', time.strftime('%Y-%m-%d', time.strptime(bank_statement['date'], "%Y/%m/%d"))), ('date_stop', '>=', time.strftime('%Y-%m-%d', time.strptime(bank_statement['date'], "%Y/%m/%d")))])
        bank_statement['period_id'] = period_id and period_id[0] or False
        bank_statements.append(bank_statement)

    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
