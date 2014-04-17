# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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
import pooler
import conversion
import string
from tools import DEFAULT_SERVER_DATE_FORMAT

def get_data(self, cr, uid, ids, recordlist, data):
    
    account_period_obj = self.pool.get('account.period')
    bank_statement_obj = self.pool.get('account.bank.statement')
    line_statement_obj = self.pool.get('account.bank.statement.line')
    journal_obj = self.pool.get('account.journal')
    journal_code = journal_obj.browse(cr, uid, data['journal_id']).code
    if not data:
        data = {}
    
    date_format = data.get('date_format') or '%Y/%m/%d'
    bank_statements = []
    i = 0        
    first_line = True
               
    total_amount = 0
    bank_statement = {}
    bank_statement_lines = {}
    bank_statement["bank_statement_line"] = {}
    line_name = 0
    st_line_name = line_name

    # Loop on all line of a month
    for line in recordlist:
        if first_line:
            first_line = False
            continue
        if len(line) <= 1:  # the end of the file has an empty line
            continue
        line_list = line.split(';')
        if line_list[1].replace('"','') == 'Date de valeur' :
            continue
           
        st_line_name = line_name
        st_line = {}
        st_line['statement_id'] = 0
        date = line_list[1].replace('"','')
#        if len(date.split("/")[2]) == 2 :
#            date = str(date.split("/")[0]) + "/" + str(date.split("/")[1]) + "/20" + str(date.split("/")[2])
        entry_date = line_list[0].replace('"','')
#        if len(entry_date.split("/")[2]) == 2 :
#            entry_date = str(entry_date.split("/")[0]) + "/" + str(entry_date.split("/")[1]) + "/20" + str(entry_date.split("/")[2])
        st_line['date'] = time.strftime(DEFAULT_SERVER_DATE_FORMAT, time.strptime(date, date_format))
        st_line['entry_date'] = time.strftime(DEFAULT_SERVER_DATE_FORMAT, time.strptime(entry_date, date_format))
        st_line['val_date'] = time.strftime(DEFAULT_SERVER_DATE_FORMAT, time.strptime(date, date_format))
        st_line['partner_id'] = 0
        st_line['type'] = 'general'
        st_line['name'] = line_list[4].replace('"','')
        st_line['free_comm'] = ''
        st_line['ref'] = ''
        st_line['extra_note'] = ''
        
        if line_list[2].replace('"',''):
            amount = line_list[2].replace(',','.')
            st_line_amt = conversion.str2float(amount)
            st_line['account_id'] = data['payable_id'][0]
        elif line_list[3].replace('"',''):
            amount = line_list[3].replace(',','.')
            st_line_amt = conversion.str2float(amount)
            st_line['account_id'] = data['receivable_id'][0]
            
        st_line['amount'] = st_line_amt
#        '''Definition of a positive or negative value'''
#        if st_line_amt.startswith('-'):
#            st_line['account_id'] = data['payable_id']
#        else:
#            st_line['account_id'] = data['receivable_id']
        
        # check of uniqueness of a field in the data base
        check_ids = line_statement_obj.search(cr, uid, [
							('amount','=',st_line_amt),
							('date','=',st_line['val_date']),
							('name','=',line_list[2].replace('"',''))])
        if check_ids:
            continue        
        if not check_ids:   
            bank_statement_lines[line_name] = st_line
            line_name += 1                    
        bank_statement["bank_statement_line"] = bank_statement_lines
        i += 1
        total_amount += st_line_amt

    # Saving data at month level
    bank_statement["total_amount"] = total_amount
    bank_statement['journal_id'] = data['journal_id'][0]
    period_id = account_period_obj.search(cr, uid, [('special','=',False),
					('date_start', '<=', st_line['date']),#time.strftime(DEFAULT_SERVER_DATE_FORMAT, time.strptime(st_line['date'], DEFAULT_SERVER_DATE_FORMAT))),
					('date_stop', '>=', st_line['date'])])#time.strftime(DEFAULT_SERVER_DATE_FORMAT, time.strptime(st_line['date'], DEFAULT_SERVER_DATE_FORMAT)))])
    bank_statement['date'] = st_line['date']#time.strftime(DEFAULT_SERVER_DATE_FORMAT,time.strptime(st_line['date'], DEFAULT_SERVER_DATE_FORMAT))
    bank_statement['period_id'] = period_id and period_id[0] or False
    bank_statements.append(bank_statement)

    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
