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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from ...string_operation import to_unicode
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

def get_data(self, recordlist):
    
    account_period_obj = self.env['account.period']
    line_obj = self.env['account.bank.statement.line']

    bank_statements = []
    pointor = 0
    total_amount = 0
    bank_statement = {}
    bank_statement_lines = {}
    bank_statement["bank_statement_line"] = {}
    
    date_format = self.date_format
    if len(recordlist) > 12:
        for line in recordlist[12:]:
            line = line.replace('"','')
            line_splited = line.split(';')
            if line_splited[0]== '':
                break
            st_line = {}
            line_name = pointor
            st_line['extra_note'] = ''
            date_1 = time.strptime(line_splited[0], date_format)
            st_line['date'] = time.strftime(DF, date_1)
            st_line['name'] = line_splited[1]
            st_line['ref'] = line_splited[2]
            amount = 0
            if line_splited[4]:
                amount = to_unicode(line_splited[4])
            if line_splited[5]:
                amount = to_unicode(line_splited[5])
            # Format conversion
            if '.' in amount:
                amount = amount.replace('.','')
    #         if '\xc2\xa0' in amount:
    #             amount = amount.replace('\xc2\xa0','')
    #         if ' ' in amount:
    #             amount = amount.replace(' ','')
            if ',' in amount:
                amount = amount.replace(',','.')
            amount = amount.split()
            amount = "".join(amount)
            
            '''Definition of a positive or negative value'''
            amount = float(amount or 0.0)
            if line_splited[4]:
                amount = - amount
            if amount < 0:
                st_line['account_id'] = self.payable_id.id
            else:
                st_line['account_id'] = self.receivable_id.id
            st_line['amount'] = amount
            st_line['partner_id'] = False
            
            # check of uniqueness of a field in the data base
            date = st_line['date']
            check_ids = line_obj.search([
                                         ('ref', '=', line_splited[1]),
                                         ('name', '=', line_splited[3]),
                                         ('date', '=', date),
                                         ('amount','=',amount)
                                         ])
            if check_ids:
                continue        
            if not check_ids:   
                bank_statement_lines[line_name] = st_line
            bank_statement["bank_statement_line"] = bank_statement_lines
            pointor += 1
            total_amount += amount

    # Saving data at month level
    bank_statement['total_amount'] = total_amount
    period_id = account_period_obj.search([
                                           ('date_start', '<=', date),
                                           ('date_stop', '>=', date)
                                           ])
    bank_statement['date'] = date
    bank_statement['period_id'] = period_id and period_id[0] or False
    bank_statements.append(bank_statement)

    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: