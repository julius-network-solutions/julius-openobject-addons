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
import pooler
import conversion


def get_data(self, cr, uid, ids, recordlist):
    
    bank_statements = []
    bank_statement = {}
    for line in recordlist:
        if line[0] == '0':
            # header data

            bank_statement["bank_statement_line"]={}
            bank_statement_lines = {}
            bank_statement['date'] = str2date(line[5:11])
            bank_statement['journal_id']=data['journal_id']
            period_id = account_period_obj.search(cr, uid, [('date_start', '<=', time.strftime('%Y-%m-%d', time.strptime(bank_statement['date'], "%y/%m/%d"))), ('date_stop', '>=', time.strftime('%Y-%m-%d', time.strptime(bank_statement['date'], "%y/%m/%d")))])
            bank_statement['period_id'] = period_id and period_id[0] or False
            bank_statement['state']='draft'
        elif line[0] == '1':
            # old balance data
            bal_start = list2float(line[43:58])
            if line[42] == '1':
                bal_start = - bal_start
            bank_statement["balance_start"]= bal_start
            bank_statement["acc_number"]=line[5:17]
            bank_statement["acc_holder"]=line[64:90]
            bank_statement['name'] = journal_code + ' ' + str(line[2:5])

        elif line[0]=='2':
            # movement data record 2
            if line[1]=='1':
                # movement data record 2.1
                if bank_statement_lines.has_key(line[2:6]):
                    continue
                st_line = {}
                st_line['extra_note'] = ''
                st_line['statement_id']=0
                st_line['ref'] = line[2:10]
                st_line['date'] = time.strftime('%Y-%m-%d', time.strptime(str2date(line[115:121]), "%y/%m/%d")),
                st_line_amt = list2float(line[32:47])

                if line[61]=='1':
                    st_line['toreconcile'] = True
                    st_line['name']=line[65:77]
                else:
                    st_line['toreconcile'] = False
                    st_line['name']=line[62:115]

                st_line['free_comm'] = st_line['name']
                st_line['val_date']=time.strftime('%Y-%m-%d', time.strptime(str2date(line[47:53]), "%y/%m/%d")),
                st_line['entry_date']=time.strftime('%Y-%m-%d', time.strptime(str2date(line[115:121]), "%y/%m/%d")),
                st_line['partner_id']=0
                if line[31] == '1':
                    st_line_amt = - st_line_amt
                    st_line['account_id'] = def_pay_acc
                else:
                    st_line['account_id'] = def_rec_acc
                st_line['amount'] = st_line_amt
                bank_statement_lines[line[2:6]]=st_line
                bank_statement["bank_statement_line"]=bank_statement_lines
            elif line[1] == '2':
                st_line_name = line[2:6]
                bank_statement_lines[st_line_name].update({'account_id': data['awaiting_account']})

            elif line[1] == '3':
                # movement data record 3.1
                st_line_name = line[2:6]
                st_line_partner_acc = str(line[10:47]).strip()
                cntry_number=line[10:47].strip()
                contry_name=line[47:125].strip()
                bank_ids = partner_bank_obj.search(cr, uid, [('acc_number', '=', st_line_partner_acc)])
                bank_statement_lines[st_line_name].update({'cntry_number': cntry_number, 'contry_name': contry_name})
                if bank_ids:
                    bank = partner_bank_obj.browse(cr, uid, bank_ids[0], context=context)
                    if line and bank.partner_id:
                        bank_statement_lines[st_line_name].update({'partner_id': bank.partner_id.id})
                        if bank_statement_lines[st_line_name]['amount'] < 0:
                            bank_statement_lines[st_line_name].update({'account_id': bank.partner_id.property_account_payable.id})
                        else:
                            bank_statement_lines[st_line_name].update({'account_id': bank.partner_id.property_account_receivable.id})
                else:
                    nb_err += 1
                    err_log += _('The bank account %s is not defined for the partner %s.\n')%(cntry_number, contry_name)
                    bank_statement_lines[st_line_name].update({'account_id': data['awaiting_account']})

                bank_statement["bank_statement_line"]=bank_statement_lines
        elif line[0]=='3':
            if line[1] == '1':
                st_line_name = line[2:6]
                bank_statement_lines[st_line_name]['extra_note'] += '\n' + line[40:113]
            elif line[1] == '2':
                st_line_name = line[2:6]
                bank_statement_lines[st_line_name]['extra_note'] += '\n' + line[10:115]
            elif line[1] == '3':
                st_line_name = line[2:6]
                bank_statement_lines[st_line_name]['extra_note'] += '\n' + line[10:100]
        elif line[0]=='8':
            # new balance record
            bal_end = list2float(line[42:57])
            if line[41] == '1':
                bal_end = - bal_end
            bank_statement["balance_end_real"]= bal_end

        elif line[0]=='9':
            # footer record

            bank_statements.append(bank_statement)
    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

