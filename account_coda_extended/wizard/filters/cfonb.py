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
    
    account_period_obj = self.pool.get('account.period')
    journal_obj = self.pool.get('account.journal')
    journal_code = journal_obj.browse(cr, uid, data['journal_id']).code
    
    bank_statements = []
    bank_statement = {}
    for line in recordlist:
        if line[0:2] == '01':
            bank_statement = {}
            bank_statement["bank_statement_line"] = {}
            bank_statement_lines = {}
            num = int(line[19:20]) or 2
            bank_statement["acc_number"] = line[21:32]
            bank_statement['date'] = conversion.str2date(line[34:40])
            bank_statement['journal_id'] = data['journal_id']
            period_id = account_period_obj.search(cr, uid, [('date_start', '<=', time.strftime('%Y-%m-%d', time.strptime(bank_statement['date'], "%y/%m/%d"))), ('date_stop', '>=', time.strftime('%Y-%m-%d', time.strptime(bank_statement['date'], "%y/%m/%d")))])
            bank_statement['period_id'] = period_id and period_id[0] or False
            bank_statement['state'] = 'draft'
            amount = line[91:104]
            amount, sign = letterconvert(amount)
            amount = list2float2(amount, num)
            bal_start = change_sign(amount, sign)
            bank_statement["balance_start"] = bal_start
#            bank_statement['name'] = False

        elif line[0:2] == '04':
            st_line = {}
            line_name = line[48:79]
            st_line['name'] = line[48:79]
            st_line['extra_note'] = line[48:79]
            st_line['ref'] = line[81:88]
            st_line['date'] = conversion.str2date(line[34:40])
            num = int(line[19:20]) or 2
            amount = line[91:104]
            amount, sign = letterconvert(amount)
            amount = list2float2(amount, num)
            amount = change_sign(amount, sign)
#            bal_start = list2float2(amount, num, sign)
            st_line['amount'] = amount
            if sign == '-':
#            if line[32:34] in ('01','11','23','96','62','67','70'):
#                st_line['amount'] = amount
                st_line['account_id'] = data['def_payable']
            elif sign == '+':
#            elif line[32:34] in ('02','05'):
#                st_line['amount'] = amount
                st_line['account_id'] = data['def_receivable']
#            else:
#                st_line['amount'] = amount
#                st_line['account_id'] = data['def_receivable']
                
            st_line['partner_id'] = False
            bank_statement_lines[line_name] = st_line
            bank_statement["bank_statement_line"] = bank_statement_lines
        elif line[0:2] == '05':
            extra = line[48:79]
            st_line['extra_note'] += '\n' + line[48:79]
        elif line[0:2] == '07':
            num = int(line[19:20]) or 2
            amount = line[91:104]
            amount, sign = letterconvert(amount)
            amount = list2float2(amount, num)
            bal_end = change_sign(amount, sign)
#            bal_end = list2float2(line[91:103], num)
            bank_statement["balance_end_real"] = bal_end
            bank_statements.append(bank_statement)
    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
