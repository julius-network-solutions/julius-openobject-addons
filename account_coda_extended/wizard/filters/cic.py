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
import pooler
import conversion
import string

#def get_data(self, cr, uid, bankData, bank_statement):
#
#	account_period_obj = self.pool.get('account.period')
#	bank_statement_obj = self.pool.get('account.bank.statement')
#	journal_obj = self.pool.get('account.journal')
#	
#    bank_statement_lines={}
#    bank_statements=[]
#    line_name = 0
#    st_line_name = line_name
#    code4 = 0
#    for line in bankData:
#        if len(line) <= 1:  # the end of the file has an empty line
#            continue
#        line_list = line.split(',')
#        if line_list[1].replace('"','') == 'Date de valeur' :
#            continue
#
#        st_line_name = line_name
#        st_line = {}
#        st_line['statement_id']=0
#        date = line_list[1].replace('"','')
#        if len(date.split("/")[2]) == 2 :
#            date = str(date.split("/")[0]) + "/" + str(date.split("/")[1]) + "/20" + str(date.split("/")[2])
#        entry_date = line_list[0].replace('"','')
#        if len(entry_date.split("/")[2]) == 2 :
#            entry_date = str(entry_date.split("/")[0]) + "/" + str(entry_date.split("/")[1]) + "/20" + str(entry_date.split("/")[2])
#        st_line['date'] = time.strftime('%Y/%m/%d',time.strptime(date,"%d/%m/%Y"))
#        st_line['entry_date'] = time.strftime('%Y-%m-%d',time.strptime(entry_date,"%d/%m/%Y"))
#        st_line['val_date'] = time.strftime('%Y-%m-%d',time.strptime(date,"%d/%m/%Y"))
#        st_line['partner_id'] = False
#        st_line['type'] = 'general'
#        st_line['name'] = line_list[4].replace('"','')
#        st_line['free_comm'] = ''
#        st_line['ref'] = ''
#        st_line['cntry_number'] = ''
#        st_line['contry_name'] = ''
#
#        if line_list[2].replace('"',''):
#            st_line_amt = conversion.str2float(line_list[2].replace('"',''))
#            st_line['account_id'] = bank_statement['def_payable']
#        elif line_list[3].replace('"',''):
#            st_line_amt = conversion.str2float(line_list[3].replace('"',''))
#            st_line['account_id'] = bank_statement['def_receivable']
#            
#        st_line['amount'] = st_line_amt
#        st_line['partner_acc_number'] = ''
#                    
##        check_ids = pool.get('account.bank.statement.line').search(cr, uid, [
##									('amount','=',st_line_amt),
##									('date','=',st_line['val_date']),
##									('name','=',line_list[2].replace('"',''))])
##    
##        if not check_ids:   
##            bank_statement_lines[line_name] = st_line
##            line_name += 1
##    # delete latest row from the list because its an empty row
##    print bank_statements
##    print bank_statement_lines
##    a = zefezg
##    if len(bank_statement_lines) >= 1:
##        #del bank_statement_lines[ line_name ]  # delete latest row from the list
##        for test in bank_statement_lines:
##            bank_statements.append(bank_statement_lines[test])
#         
#      # count the end balance
##      for value in bank_statement_lines:
##         line=bank_statement_lines[value]
##         bal_end += line['amount']
#
##      bank_statement["balance_end_real"]= bal_end
##      bank_statement["bank_statement_line"]=bank_statement_lines
#        check_ids = self.pool.get('account.bank.statement.line').search(cr,uid,[('name','=',line_splited[1]),('date','=',line_splited[2]),('amount','=',amount)])
#        if check_ids:
#            continue		
#        if not check_ids:   
#            bank_statement_lines[line_name]=st_line
#            line_name += 1
#        bank_statement["bank_statement_line"] = bank_statement_lines
#        i += 1
#        total_amount += amount
#
#    # Saving data at month level
#    bank_statement["total_amount"] = total_amount
#    bank_statement['journal_id'] = data['journal_id']
#    period_id = account_period_obj.search(cr, uid, [('date_start', '<=', time.strftime('%Y-%m-%d', time.strptime(st_line['date'], "%d/%m/%Y"))), ('date_stop', '>=', time.strftime('%Y-%m-%d', time.strptime(st_line['date'], "%d/%m/%Y")))])
#    bank_statement['date'] = time.strftime('%Y/%m/%d',time.strptime(st_line['date'], "%d/%m/%Y"))
#    bank_statement['period_id'] = period_id and period_id[0] or False
#    bank_statements.append(bank_statement)
#     
#    return bank_statements

def get_data(self, cr, uid, ids, recordlist, data):
    
    account_period_obj = self.pool.get('account.period')
    bank_statement_obj = self.pool.get('account.bank.statement')
    line_statement_obj = self.pool.get('account.bank.statement.line')
    journal_obj = self.pool.get('account.journal')
    journal_code = journal_obj.browse(cr, uid, data['journal_id']).code
    
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
        line_list = line.split(',')
        if line_list[1].replace('"','') == 'Date de valeur' :
            continue
           
        st_line_name = line_name
        st_line = {}
        st_line['statement_id'] = 0
        date = line_list[1].replace('"','')
        if len(date.split("/")[2]) == 2 :
            date = str(date.split("/")[0]) + "/" + str(date.split("/")[1]) + "/20" + str(date.split("/")[2])
        entry_date = line_list[0].replace('"','')
        if len(entry_date.split("/")[2]) == 2 :
            entry_date = str(entry_date.split("/")[0]) + "/" + str(entry_date.split("/")[1]) + "/20" + str(entry_date.split("/")[2])
        st_line['date'] = time.strftime('%Y/%m/%d', time.strptime(date, "%d/%m/%Y"))
        st_line['entry_date'] = time.strftime('%Y-%m-%d', time.strptime(entry_date, "%d/%m/%Y"))
        st_line['val_date'] = time.strftime('%Y-%m-%d', time.strptime(date, "%d/%m/%Y"))
        st_line['partner_id'] = 0
        st_line['type'] = 'general'
        st_line['name'] = line_list[4].replace('"','')
        st_line['free_comm'] = ''
        st_line['ref'] = ''
        st_line['cntry_number'] = ''
        st_line['contry_name'] = ''
        st_line['extra_note'] = ''
        
        if line_list[2].replace('"',''):
            st_line_amt = conversion.str2float(line_list[2].replace('"',''))
            st_line['account_id'] = data['def_payable'][0]
        elif line_list[3].replace('"',''):
            st_line_amt = conversion.str2float(line_list[3].replace('"',''))
            st_line['account_id'] = data['def_receivable'][0]

        st_line['amount'] = st_line_amt
        
#        '''Definition of a positive or negative value'''
#        if st_line_amt.startswith('-'):
#            st_line['account_id'] = data['def_payable']
#        else:
#            st_line['account_id'] = data['def_receivable']
        
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
    period_id = account_period_obj.search(cr, uid, [
					('date_start', '<=', time.strftime('%Y-%m-%d', time.strptime(st_line['date'], "%Y/%m/%d"))),
					('date_stop', '>=', time.strftime('%Y-%m-%d', time.strptime(st_line['date'], "%Y/%m/%d")))])
    bank_statement['date'] = time.strftime('%Y/%m/%d',time.strptime(st_line['date'], "%Y/%m/%d"))
    bank_statement['period_id'] = period_id and period_id[0] or False
    bank_statements.append(bank_statement)

    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
