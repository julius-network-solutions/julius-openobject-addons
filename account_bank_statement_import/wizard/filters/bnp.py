# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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
###############################################################################

import time
from openerp.exceptions import Warning

def get_data(self, recordlist):
    separator = self.get_separator()
    name = self.get_column_number(self.column_name, 2)
    date = self.get_column_number(self.column_date, 0)
    date_val = self.get_column_number(self.column_date_val, 0)
    debit = self.get_column_number(self.column_debit, 3)
    credit = self.get_column_number(self.column_credit, 4)
    ignored_lines = self.ignored_lines or 5
    separated_amount = self.amount_separated
    date_format = self.date_format
    receivable_id = self.receivable_id.id
    payable_id = self.payable_id.id
    many_statements = self.many_statements
    default_key = time.strftime('%Y-%m')
    statement_date = False
    
    ## Get Ending Balance ##
    result = self.format_statement_from_data(recordlist, separator,
                                           date_format=date_format,
                                           many_statements=many_statements,
                                           ignored_lines=ignored_lines,
                                           name=name, date=date,
                                           date_val=date_val,
                                           debit=debit, credit=credit,
                                           separated_amount=separated_amount,
                                           receivable_id=receivable_id,
                                           payable_id=payable_id, ref=False,
                                           extra_note=False,
                                           statement_date=False,
                                           default_key=default_key)
    for statement in result:
        if not many_statements:
            statement.update({'balance_end_real':recordlist[0].split(separator)[2]})
        else:
            raise Warning(('Bad configuration should not use this mode !'))
    return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
