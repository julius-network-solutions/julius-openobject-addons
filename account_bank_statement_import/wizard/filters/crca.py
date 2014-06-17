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

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
import time

def get_data(self, cr, uid, ids, recordlist, data):
    
    account_period_obj = self.pool.get('account.period')
    bank_statement_obj = self.pool.get('account.bank.statement')
    journal_obj = self.pool.get('account.journal')
    journal_code = journal_obj.browse(cr, uid, data['journal_id']).code
    
    bank_statements = []
    i = 0        
    bal_end = 0
    month_statement = {}
    
    import_line = False
    label = False
    date_format = data.get('date_format') or '%d/%s/%Y'
    for line in recordlist:
        line_splited = line.split(';')
        if not import_line:
            if line_splited[0] == 'Date' and line_splited[1] == 'Date valeur':
                import_line = True
            continue
        if label == False:
            if len(line_splited) == 3:
                date, date_value, line_name = line_splited
                if line_name.startswith('"'):
                    line_name = line_name[1:]
                label = True
                continue
            elif len(line_splited) == 5:
                date, date_value, line_name, debit, credit = line_splited
        else:
            if len(line_splited) == 1:
                name_continue = line_splited[0]
                line_name += '\n' + name_continue
                continue
            else:
                label = False
                if len(line_splited) == 3:
                    name_continue, debit, credit = line_splited
                elif len(line_splited) == 4:
                    name_continue, debit, credit, empty = line_splited
                if name_continue.endswith('"'):
                    name_continue = name_continue[:-1]
                line_name += '\n' + name_continue
        
        if import_line and len(line_splited) == 1 and (line_splited[0] in ('\r', '  \r')):
            break
        period = time.strftime('%Y-%m', time.strptime(date, date_format))
        month_statement.setdefault(period, [])
        month_statement[period].append({
            'date': date,
            'date_value': date_value,
            'line_name': line_name,
            'debit': debit,
            'credit': credit,
            })
    
    # loop on each month
    for key in month_statement.keys():
               
        total_amount = 0
        bank_statement = {}
        bank_statement_lines = {}
        bank_statement["bank_statement_line"] = {}
        
         # Loop on all line of a month
        for line_dict in month_statement[key]:
            st_line = {}
            line_name = i
            name = line_dict.get('line_name') or ''
            debit = line_dict.get('debit') or 0
            credit = line_dict.get('credit') or 0
            date = line_dict.get('date') or ''
            date_value = line_dict.get('date_value') or ''
            
            amount = 0
            '''Definition of a positive or negative value'''
            if debit:
                st_line['account_id'] = data['payable_id'][0]
                amount = debit
                amount = float(amount.replace(',', '.') or 0.0)
                amount = -amount
            elif credit:
                st_line['account_id'] = data['receivable_id'][0]
                amount = credit
                amount = float(amount.replace(',', '.') or 0.0)
            
            st_line['amount'] = amount
            st_line['partner_id'] = False
            st_line['name'] = name
            st_line['date'] = date
            st_line['extra_note'] = _('Value date: %s') % date_value
            
            # check of uniqueness of a field in the data base            
            check_ids = self.pool.get('account.bank.statement.line').search(cr, uid, [
                    ('name', '=', name),
                    ('date', '=', date),
                    ('amount', '=', amount),
                ])
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
        bank_statement['date'] = time.strftime('01/%m/%Y', time.strptime(key,"%Y-%m"))
        period_id = account_period_obj.search(cr, uid, [
                ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT, time.strptime(bank_statement['date'], date_format))),
                ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT, time.strptime(bank_statement['date'], date_format)))
            ], limit=1)
        bank_statement['period_id'] = period_id and period_id[0] or False
        bank_statements.append(bank_statement)
    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
