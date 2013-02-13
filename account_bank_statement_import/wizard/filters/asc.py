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
# This filter imports .asc-files (BRI-layout).
#

from osv import fields, osv
import time
import pooler
import conversion
import string

def get_data(self, cr, uid, ids,  bankData, bank_statement):
	   
      pool = pooler.get_pool(cr.dbname)
      
      bal_end = bank_statement['bal_end']
      bank_statement_lines={}
      bank_statements=[]
      line_name = 0
      st_line_name = line_name
      code4 = 0
      
      # parse every line in the file and get the right data
      for line in bankData:
         if len(line) <= 23:  # the end of the file has an empty line
            pass
         else:
            # check if bankaccount in the file matches with the bankaccount of the database
            bankaccount = line[0:10]
            # Look if we can match our number with a number in the list
            if bankaccount.lower() in bank_statement["acc_number"]:
               # look for the recordtype
               # 2 is the baserecord. We can also have 3 and 4. These are followrecords.
               if line[23] == '2' and code4 == 0:
                  st_line_name = line_name
                  st_line = {}
                  st_line['statement_id']=0
                  st_line['name'] = line[48:72]
                  st_line['date'] = conversion.str2date(line[87:93]) # boekingsdatum
                  st_line_amt = conversion.list2float(line[73:86])
                  
                  if line[86] == "D": 
                     st_line_amt = - st_line_amt
                     st_line['account_id'] = bank_statement['def_pay_acc']
                  else:
                     st_line['account_id'] = bank_statement['def_rec_acc']
                    
                  st_line['entry_date']=time.strftime('%Y-%m-%d',time.strptime(conversion.str2date(line[87:93]),"%d/%m/%y")),
                  st_line['val_date']=time.strftime('%Y-%m-%d',time.strptime(conversion.str2date(line[93:99]),"%d/%m/%y")),
                              
                  st_line['partner_id']=0
                  st_line['amount'] = st_line_amt
                  st_line['type'] = 'general'
                 
                  st_line_partner_acc = str(line[38:48]).strip()
                  if st_line_partner_acc[:1] == '0':
                  	st_line_partner_acc = st_line_partner_acc[1::]
                  	
                  st_line['partner_acc_number'] = st_line_partner_acc 
                  	 	  
                  cntry_number=st_line_partner_acc
                  contry_name=line[48:72]
                  bank_ids = pool.get('res.partner.bank').search(cr,uid,[('acc_number','=',st_line_partner_acc)])
                  
                  if bank_ids:
                     bank = pool.get('res.partner.bank').browse(cr,uid,bank_ids[0],context={})
                     st_line['cntry_number']=cntry_number
                     st_line['contry_name']=contry_name
      
                     if st_line and bank.partner_id:
                        st_line['partner_id']=bank.partner_id.id
                        
                        # Create a check if we don't already imported this statement
                        # We make an unique check in the database with
                        # partner, date and amount
                        check_ids = pool.get('account.bank.statement.line').search(cr,uid,[('amount','=',st_line_amt), ('date','=',st_line['entry_date']),('partner_id','=',bank.partner_id.id)])
                                         
                                
                        # check if the partner is a supplier or customer
                        # if both, we don't add a account due to credit invoices		
                        partner = pool.get('res.partner').browse(cr,uid,bank.partner_id,context={})
                        
                        st_line['type']='general'
                        
                        if bank.partner_id.supplier == True and bank.partner_id.customer == False:
                        	st_line['account_id']= bank.partner_id.property_account_receivable.id
                        	st_line['type']='supplier'

                        elif bank.partner_id.customer == True and bank.partner_id.supplier == False :
                        	st_line['account_id']= bank.partner_id.property_account_payable.id
                        	st_line['type']='customer'

                        #if st_line['amount'] < 0 :
                        #   st_line['account_id']= bank.partner_id.property_account_payable.id
                        #else :
                        #   st_line['account_id']= bank.partner_id.property_account_receivable.id
   
                  else:
                     st_line['cntry_number']=cntry_number
                     st_line['contry_name']=contry_name
                     
                     # Create a check if we don't already imported this statement
                     # We make an unique check in the database with
                     # name, date and amount
                     check_ids = pool.get('account.bank.statement.line').search(cr,uid,[('amount','=',st_line_amt), ('date','=',st_line['entry_date']), ('name','=',contry_name)])               
                 
                  st_line['free_comm']= ''
                  st_line['ref']=''
                
               elif line[23] == '3' and code4 == 0 :      # get some information about the transaction
                  st_line['free_comm']=line[56:119]
                  refe = line[56:119].split(' ')
                  stri = ''
                  for t in refe:
                  	if t.strip():
                        	stri = stri + ' ' + ''.join(t.strip())
                  
                  st_line['ref']=stri
                  code4 = int(line[120])
                  if not check_ids:
                     line_name += 1
                     st_line_name = line_name      
                     
               elif line[23] == '4':      # get some more information about the transaction
                  st_line['free_comm'] = st_line['free_comm'] + "\n" + line[24:119]
                  code4 = code4 - 1
               
               if not check_ids:   
                 bank_statement_lines[line_name]=st_line
               #  bank_statements.append(st_line)    
         

           # end if
      # end for
      
      
      
      # delete latest row from the list because its an empty row
      if len(bank_statement_lines) >= 1:
         del bank_statement_lines[ line_name ]  # delete latest row from the list
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
