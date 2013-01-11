##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) and Eddy Boer
#                          All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#                    Eddy Boer <tinyerp@EdbO.xs4all.nl>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
# I used the code of account_coda as base for this module. The module does
# exactly the same thing as account_coda. The difference is the file-layout. 
#
# This filter imports .coda-files (CODA-layout).
#


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
    bal_end = 0
    first_line = True
    month_statement = {}
    month_statement_period = {}
    
    # first loop on each line to determine the number of month in the statement
    for line_1 in recordlist:
        line_splited_1 = line_1.split('\t') 
        if first_line:
            bal_end = float(line_splited_1[2] or 0.0)            
            first_line = False
            continue
               
        st_line_1 = {}
        st_line_1['date'] = line_splited_1[2]
        
        line_period = time.strftime('%Y-%m', time.strptime(st_line_1['date'], "%Y/%m/%d"))
       
        if line_period in month_statement.keys():
            month_statement[line_period].append(line_1)
        else:
            month_statement[line_period] = [line_1]
            month_statement_period[line_period] = line_period
        
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
            st_line['date'] = line_splited[2]
            st_line['name'] = line_splited[1]
            st_line['extra_note'] = ''
            st_line['ref'] = ''
            amount = line_splited[3]
            
            '''Definition of a positive or negative value'''
            if amount.startswith('-'):
                st_line['account_id'] = data['def_payable'][0]
            else:
                st_line['account_id'] = data['def_receivable'][0]
                
            amount = float(amount or 0.0)
            st_line['amount'] = amount
            st_line['partner_id'] = False
            
            # check of uniqueness of a field in the data base            
            check_ids = self.pool.get('account.bank.statement.line').search(cr,uid,[('name','=',line_splited[1]),('date','=',line_splited[2]),('amount','=',amount)])
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
