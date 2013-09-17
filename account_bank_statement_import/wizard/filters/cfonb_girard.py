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

import time
import conversion
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

list_positive = {
                 '{': '0',
                 'A': '1',
                 'B': '2',
                 'C': '3',
                 'D': '4',
                 'E': '5',
                 'F': '6',
                 'G': '7',
                 'H': '8',
                 'I': '9',
                 }

list_negative = {
                 '}': '0',
                 'J': '1',
                 'K': '2',
                 'L': '3',
                 'M': '4',
                 'N': '5',
                 'O': '6',
                 'P': '7',
                 'Q': '8',
                 'R': '9',
                 }

def list2float2(lst, num=2):
    try:
        return conversion.str2float((lambda s : s[:-num] + '.' + s[-num:])(lst))
    except:
        return 0.0
    
def letterconvert(lst):
    letter = lst[-1:]
    if letter in list_positive.keys():
        val = list_positive[letter]
        sign = '+'
        lst = lst.replace(letter, val)
        return lst, sign 
    elif letter in list_negative.keys():
        val = list_negative[letter]
        sign = '-'
        lst = lst.replace(letter, val)
        return lst, sign
    else:
        lst = lst.replace(letter, '0')
    return lst, '+'

def change_sign(amount, sign='+'):
    if sign == '-':
        amount = - amount
    return amount

def get_data(self, cr, uid, ids, recordlist, data):
    
    ## Initialization ##
    account_period_obj = self.pool.get('account.period')
    date_format = str(self.pool.get('account.bank.statement.import').browse(cr, uid, ids[0]).date_format)
    
    pointor = 0
    
    bank_statements = []
    bank_statement = {}
    bank_statement_lines = {}
    bank_statement["bank_statement_line"] = {}
    
    ## Process ##
    for line in recordlist:
        ## First Line Special Process ##
        if line[0:2] == '01':
            
            bank_statement['date'] = time.strftime( '%m/%d/%Y', time.strptime(line[34:40], date_format))
            
            ## Balance Start Computation ##
            num = int(line[19:20]) or 2
            amount = line[91:104]
            amount, sign = letterconvert(amount)
            amount = list2float2(amount, num)
            bal_start = change_sign(amount, sign)
            bank_statement["balance_start"] = bal_start
        ## Bank Account Line ##
        elif line[0:2] == '04':
            st_line = {}
            line_name = pointor
            st_line['ref'] = line[81:88]
            st_line['name'] = line[48:79]
            st_line['date'] = time.strftime( '%m/%d/%Y', time.strptime(line[34:40], date_format))
            st_line['extra_note'] = ''
            st_line['partner_id'] = False
            ## Value Computation ##
            num = int(line[19:20]) or 2
            amount = line[91:104]
            amount, sign = letterconvert(amount)
            amount = list2float2(amount, num)
            amount = change_sign(amount, sign)
            st_line['amount'] = amount
            if sign == '-':
                st_line['account_id'] = data['payable_id'][0]
            elif sign == '+':
                st_line['account_id'] = data['receivable_id'][0]
            ## End of Value Computation ##    
            
            ## check of uniqueness of a line in the data base ##       
            check_ids = self.pool.get('account.bank.statement.line').search(cr,uid,[
                    ('ref','=',st_line['ref']),
                    ('name','=',st_line['name']),
                    ('date','=',st_line['date']),
                    ('amount','=',amount)
                ])
            if check_ids:
                continue        
            if not check_ids:   
                bank_statement_lines[line_name] = st_line
            pointor += 1
            ## End of check ##
        
        ## Extra comment Added to the last Line ##    
        elif line[0:2] == '05':
            st_line['extra_note'] += '\n' + line[48:79]
            
        ## Last Line Special Process ##
        elif line[0:2] == '07':
            ## Balance End Computation ##
            num = int(line[19:20]) or 2
            amount = line[91:104]
            amount, sign = letterconvert(amount)
            amount = list2float2(amount, num)
            bal_end = change_sign(amount, sign)
            bank_statement["balance_end_real"] = bal_end
    ## Saving data at month level ##    
    bank_statement['total_amount'] = bank_statement["balance_end_real"] - bank_statement["balance_start"]
    bank_statement["bank_statement_line"] = bank_statement_lines
    period_id = account_period_obj.search(cr, uid, [
            ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT, time.strptime(st_line['date'], '%m/%d/%Y'))), 
            ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT, time.strptime(st_line['date'], '%m/%d/%Y'))),
        ])
    bank_statement['period_id'] = period_id and period_id[0] or False
    bank_statement['journal_id'] = data['journal_id'][0]
    bank_statements.append(bank_statement)
        
    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
