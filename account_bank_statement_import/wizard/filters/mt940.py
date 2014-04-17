##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) and Peter Dapper
#                          All Rights Reserved.
#                     Peter Dapper <verkoop@of-is.nl>
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
#
# This filter imports .mt940-files 
#

from osv import fields, osv
import time
import pooler
import conversion
import string
import copy

def get_acc_number(statement_line):
	pointer = 0
	only_acc = ""
	result=[]
	# one of my suppliers uses incasso, and does not use white space in .940 file between bank account and name 
	while statement_line[pointer]!= " " and statement_line[pointer]!= "C" and statement_line[pointer]!= "D" and statement_line[pointer]!= "Q":
		only_acc = only_acc+statement_line[pointer]
		pointer += 1
	return only_acc


def get_number(statement_line):
	pointer = 7
	only_amount = ""
	while statement_line[pointer] in ["0","1","2","3","4","5","6","7","8","9",","]:
		only_amount = only_amount+statement_line[pointer]
		pointer += 1
	only_amount = only_amount.replace(",",".")
	return only_amount



def parse_sequence(bank_statement,bank, cr, uid,):
	pool = pooler.get_pool(cr.dbname)
	st_line = {}
	bank_statement_output=[]
	current=0
	while current < len(bank_statement):
		#if ':61:' in bank_statement[current]:
		if bank_statement[current].has_key(':61:'):
			# Pfff.. a line we can use. Gives us the date, debit/credit, and amount
			st_line['date']=conversion.str2date(bank_statement[current][':61:'][0:6])
			entry_date = time.strftime('%Y-%m-%d',time.strptime(conversion.str2date(bank_statement[current][':61:'][0:6]),"%d/%m/%y")),
			st_line['val_date']   = time.strftime('%Y-%m-%d',time.strptime(conversion.str2date(bank_statement[current][':61:'][0:6]),"%d/%m/%y")),
			st_line['entry_date']=entry_date
			# Pfff...get amount
			amount =round(float(get_number(bank_statement[current][':61:'])),2)
			st_line['amount']=amount
			# Getting rich or poor
			if bank_statement[current][':61:'][6] == "D":
				st_line['account_id'] = bank['def_pay_acc']
				st_line['amount'] = - st_line['amount']
				# chek_ids did not work correctly because the amount could also be negativ
				amount = - amount
			else:
				st_line['account_id'] = bank['def_rec_acc']
			# Well, that was the transaction, now the details, directly next line..
			current += 1
			if bank_statement[current].has_key(':68:'):
				st_line['free_comm'] = " "
				st_line['partner_id'] = 0
				st_line['type'] = 'general'
				st_line['free_comm'] = " "
				st_line['partner_acc_number'] = get_acc_number(bank_statement[current][':68:'])
				st_line['cntry_number'] = get_acc_number(bank_statement[current][':68:'])
				st_line['contry_name'] =bank_statement[current][':68:'][len(st_line['cntry_number']):]
				st_line['name'] = bank_statement[current][':68:'][len(st_line['cntry_number']):]
				st_line['ref'] =" " # Sometimes .. there is no ref. Still, it is being used by other scripts.
				# Houston, we have a problem.. ING uses nicely a second :86: code, Postbank does not ... (back to the filling of the list,.done)
				# See if we have a next rule, only description!! 
				current += 1
				if bank_statement[current].has_key(':68:'):
					st_line['ref'] =bank_statement[current][':68:'][0:]
					# extra comment.. filling the free_comm
					current += 1
					if bank_statement[current].has_key(':68:'):
						st_line['free_comm'] = bank_statement[current][':68:'][0:]
					else:
						current -= 1
			# check if there is already a statement like this...
			check_ids = pool.get('account.bank.statement.line').search(cr,uid,[('amount','=',amount), ('date','=',entry_date),('name','=',st_line['name'])])
			# check if there already is a relation ..., and use the ID
			bank_ids = pool.get('res.partner.bank').search(cr,uid,[('acc_number','=',st_line['partner_acc_number'])])
			if bank_ids:
				bank = pool.get('res.partner.bank').browse(cr,uid,bank_ids[0],context={})
				if bank.partner_id:
					st_line['partner_id'] = bank.partner_id.id
					partner = pool.get('res.partner').browse(cr,uid,bank.partner_id,context={})
					if bank.partner_id.supplier == True and bank.partner_id.customer == False:
						st_line['account_id'] = bank.partner_id.property_account_receivable.id
						st_line['type'] ='supplier'
					elif bank.partner_id.customer == True and bank.partner_id.supplier == False :
						st_line['account_id'] = bank.partner_id.property_account_payable.id
						st_line['type'] ='customer'
			# ..Let see if we can make that just one line of imput
			if not check_ids:
				bank_statement_output.append(st_line.copy())
							
				
			
		current += 1
	return bank_statement_output


def fill_simple_list(bankData):
	current = 0
	bank_statement_lines={}
	bank_statements_list=[]
	while current < len(bankData):
		# codes used are 20,25,28,28c,60m,61,86,62,64,65. Only 61 and 68 are intresting (if you want more checks 25 and 60 are intresting)
		statement_line = string.find(bankData[current], ':61:')
		statement_description = string.find(bankData[current], ':86:')
		# these codes we use to determin the possible end of the description
		closing_balance = string.find(bankData[current], ':62F:')
		closing_balance_available = string.find(bankData[current], ':64:')
		if statement_line >= 0:
			bank_statement_lines[":61:"]=bankData[current][4:]
		if statement_description >= 0:
			bank_statement_lines[":68:"]=bankData[current][4:]
		if closing_balance >= 0:
			bank_statement_lines[":62F:"]=bankData[current][5:]
		if closing_balance_available >= 0:
			bank_statement_lines[":64:"]=bankData[current][4:]
		if bankData[current][0]!=":" and bankData[current][0]!="-" :
			# some banks use LF , an not an extra :68:, so mutch for a standerd
			bank_statement_lines[":68:"]=bankData[current][0:]
		if  statement_line >= 0 or statement_description >= 0 or statement_description >= 0 or closing_balance_available>= 0:	
			bank_statements_list.append(bank_statement_lines.copy())
		bank_statement_lines={}
		current += 1
	return bank_statements_list


def get_data(self, cr, uid, ids, bankData, bank_statement):
	#pool = pooler.get_pool(cr.dbname)
	bank_statement_list=[]
	bank_statement_output=[]
	bank_statement_list = fill_simple_list(bankData) #just keeping it simple
	bank_statement_output=parse_sequence(bank_statement_list,bank_statement,cr, uid,)
	return bank_statement_output


