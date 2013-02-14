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



def get_data(self, cr, uid, ids, bankData, bank_statement):
	   
    pool = pooler.get_pool(cr.dbname)


    bal_end = bank_statement['bal_end']
    bank_statement_lines={}
    bank_statements=[]
    line_name = 0
    st_line_name = line_name
    code4 = 0
    bankaccount = ''
    bankaccount = bankData[0][14:35]
    # parse every line in the file and get the right data
    if bankaccount.lower() in bank_statement["acc_number"]:
        for line in bankData:
            if len(line) <= 1:  # the end of the file has an empty line
                continue
            if line[0] != '2' :
                continue
            #else:
                #if line.count("\r") :
                #    pos=line.index("\r")
                #else :
               #     pos=0

                #if pos :
                    #i=pos-1
                    #am2 = am1 = 0
                    #char = line[i]

            st_line_name = line_name
            st_line = {}
            st_line['statement_id']=0
            line_list=line.split('	')
            #st_line['date'] =            
            #st_line['entry_date']=time.strftime('%Y-%m-%d',time.strptime(conversion.str2date(line_list[0]),"%y/%m/%d"))
            #st_line['val_date']=time.strftime('%Y-%m-%d',time.strptime(conversion.str2date(line_list[1]),"%y/%m/%d"))
            st_line['date'] = time.strftime('%d/%m/%y',time.strptime(line_list[0],"%Y/%m/%d"))
            st_line['entry_date']= time.strftime('%Y-%m-%d',time.strptime(line_list[0],"%Y/%m/%d"))
            st_line['val_date']= time.strftime('%Y-%m-%d',time.strptime(line_list[1],"%Y/%m/%d"))
            st_line['partner_id']=0
            st_line['type'] = 'general'
            st_line['name'] = line_list[2]
            st_line['free_comm']= ''
            st_line['ref']=''
     
            if line_list[4] == ' \r' :
                st_line_amt = - conversion.str2float(line_list[3])
                st_line['account_id'] = bank_statement['def_pay_acc']
            else:
            	st_line_amt = conversion.str2float(line_list[4])
                st_line['account_id'] = bank_statement['def_rec_acc']
            
            st_line['amount'] = st_line_amt
            st_line_partner_acc = bankaccount.lower()
            st_line['partner_acc_number'] = ''
            #bank_ids = pool.get('res.partner.bank').search(cr,uid,[('acc_number','=',st_line_partner_acc)])
            
            check_ids = pool.get('account.bank.statement.line').search(cr,uid,[('amount','=',st_line_amt), ('date','=',st_line['entry_date']), ('name','=',line_list[2])])
        
            if not check_ids:   
                bank_statement_lines[line_name]=st_line
                line_name += 1
         #  bank_statements.append(st_line)    
   

     # end if
# end for
      
      
      
      # delete latest row from the list because its an empty row
    if len(bank_statement_lines) >= 1:
        #del bank_statement_lines[ line_name ]  # delete latest row from the list
        for test in bank_statement_lines:
            bank_statements.append(bank_statement_lines[test])
         
      # count the end balance
#      for value in bank_statement_lines:
#         line=bank_statement_lines[value]
#         bal_end += line['amount']

#      bank_statement["balance_end_real"]= bal_end
#      bank_statement["bank_statement_line"]=bank_statement_lines
     
    return bank_statements
                
            
    #end for         
#select distinct b.partner_id, p.ref from res_partner_bank b, res_partner p where b.bank='51' and b.partner_id = p.id
