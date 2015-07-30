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

import base64
import re

from ..string_operation import (str2date, to_unicode,
                                get_key_from_date, str2float)
from openerp import fields, models, api, exceptions, _

from ..bank_statement import COLUMNS


SEPARATOR = {'comma': ',', 'semicolon': ';', 'tab': '\t', 'space': ' ', 'pipe': '|'}

class account_bank_statement_import(models.TransientModel):
    _name = "account.bank.statement.import"
    _description = "Bank statement import"

    def _default_filter_id(self, cr, uid, context=None):
        """ This method will return the default value 
        for the filter from the definition of the company."""
        if context is None: context = {}
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, context=context)
        if company_id:
            company = company_obj.browse(cr, uid, company_id)
            if company and company.def_filter_id:
                return company.def_filter_id.id
        return False

    many_journals = fields.Boolean('Many Journals', default=False,
                                   help="If you check this, the journal "\
                                   "will be use as default journal if the "\
                                   "journal is not found in the file")
    journal_id = fields.Many2one('account.journal', 'Bank Journal',
                                 required=True)
    payable_id = fields.Many2one('account.account', 'Payable Account',
                                 domain=[('type', '=', 'payable')],
                                 help="Set here the payable account that "\
                                 "will be used by default, if the partner "\
                                 "is not found")
    receivable_id = fields.Many2one('account.account', 'Receivable Account',
                                    domain=[('type', '=', 'receivable')],
                                    help="Set here the receivable account "\
                                    "that will be used by default, if the "\
                                    "partner is not found",)
    awaiting_id = fields.Many2one('account.account',
                                  'Account for Unrecognized Movement',
                                  domain=[('type', '=', 'liquidity')],
                                  help="Set here the default account that "\
                                  "will be used if the partner is found but "\
                                  "does not have the bank account, or if he "\
                                  "is domiciled",)
    filter_id = fields.Many2one('account.bankimport.filters', 'Filter',
                                required=True)
    statement_update = fields.Boolean('Update Statement', default=False)
    fill_accounts = fields.Boolean('Fill accounts', default=False)
    many_statements = fields.Boolean('Import in many Statements', default=True)
    date_format = fields.Char('Date Format', size=32, required=True)
    file_data = fields.Binary('File to import', required=True)
    note = fields.Text('Log')
    separator = fields.Selection([
                                  ('comma', 'Comma'),
                                  ('semicolon', 'Semicolon'),
                                  ('tab', 'Tab'),
                                  ('space', 'Space'),
                                  ('pipe', 'Pipe'),
                                  ('other', 'Other'),
                                  ], 'Separator')
    separator_other = fields.Char('Separator')
    ignored_lines = fields.Integer('Number of lines to ignore')
    amount_separated = fields.Boolean('Credit and Debit separated')
    column_name = fields.Selection(COLUMNS, 'Name column')
    column_date = fields.Selection(COLUMNS, 'Date column')
    column_date_val = fields.Selection(COLUMNS, 'Date of value column')
    column_debit = fields.Selection(COLUMNS, 'Debit column')
    column_credit = fields.Selection(COLUMNS, 'Credit column')
    column_ref = fields.Selection(COLUMNS, 'Ref column')
    column_note = fields.Selection(COLUMNS, 'Note column')
    edit_parameters = fields.Boolean('Edit Parameters', default=False)
    encoding = fields.Selection([
                                 ('utf-8', 'UTF-8'),
                                 ('utf-16', 'UTF-16'),
                                 ('windows-1252', 'Windows-1252'),
                                 ('latin1', 'Latin1'),
                                 ('latin2', 'Latin2'),
                                 ('big5', 'Big5'),
                                 ('gb18030', 'Gb18030'),
                                 ('shift_jis', 'Shift-JIS'),
                                 ('windows-1251', 'Windows-1251'),
                                 ('koir8_r', 'Koir8-R'),
                                 ('other', 'Other'),
                                 ], 'Encoding')
    encoding_other = fields.Char('Encoding')
    thousand_separator = fields.Char('Thousand Separator')
    text_separator = fields.Char('Text Separator')

    _defaults = {
        'filter_id': lambda self, cr, uid, context:
            self._default_filter_id(cr, uid, context),
        }

    @api.onchange('filter_id', 'fill_accounts')
    def onchange_filter_id(self):
        filter = self.filter_id
        if not self.fill_accounts:
            self.payable_id = False
            self.receivable_id = False
            self.awaiting_id = False
        else:
            self.payable_id = filter.def_payable_id.id
            self.receivable_id = filter.def_receivable_id.id
            self.awaiting_id = filter.def_awaiting_id.id
        self.many_journals = filter.many_journals
        self.journal_id = filter.def_bank_journal_id.id
        self.date_format = filter.def_date_format
        self.separator = filter.separator
        self.separator_other = filter.separator_other
        self.ignored_lines = filter.ignored_lines
        self.column_name = filter.column_name
        self.column_date = filter.column_date
        self.column_date_val = filter.column_date_val
        self.amount_separated = filter.amount_separated
        self.column_debit = filter.column_debit
        self.column_credit = filter.column_credit
        self.column_ref = filter.column_ref
        self.column_note = filter.column_note
        self.encoding = filter.encoding or 'utf-8'
        self.encoding_other = filter.encoding_other
        self.thousand_separator = filter.thousand_separator
        self.text_separator = filter.text_separator


    @api.model
    def _get_line_vals(self, line, bank_sts, str_not1):
        return {
            'name': line.get('name') or '',
            'date': line.get('date') or False,
            'amount': line.get('amount') or 0,
            'account_id': line.get('account_id') or False,
            'partner_id': line.get('partner_id') or False,
            'statement_id': bank_sts.id,
            'note': (str_not1 and (str_not1 + '\n') or '') + \
                line.get('extra_note', ''),
            'ref': line.get('ref') or '',
        }

    @api.model
    def _create_bank_statement_line(self, statement, bank_sts, fill_accounts):
        line_obj = self.env['account.bank.statement.line']
        lines = statement.get('bank_statement_line') or {}
        str_not1 = ''
        for key in lines.keys():
            line = lines[key]
            if line.has_key('contry_name') and line.has_key('cntry_number'):
                str_not1 += "Partner name:%s \n Partner Account Number:%s \n"\
                "Communication:%s \n Value Date:%s \n"
                "Entry Date:%s \n" %(line["contry_name"],
                                     line["cntry_number"],
                                     line["free_comm"]+line['extra_note'],
                                     line["val_date"][0],
                                     line["entry_date"][0])
            line_vals = self.\
                _get_line_vals(line, bank_sts, str_not1)
            if not fill_accounts:
                line_vals.pop('account_id')
            line_id = line_obj.create(line_vals)
        return str_not1

    @api.multi
    def get_file(self, recordlist):
        # based on the filter we parse the document
        filter_name = self.filter_id.filter
        filter_location = self.filter_id.filter_location or ".filters"
        exec "from " + filter_location + " import " + filter_name + " as parser"
        # opening the file speficied as bank_file and read the data
        try:
            bank_statements = parser.get_data(self, recordlist)
        except IOError:
            raise
        return bank_statements

    @api.model
    def _get_statement_vals(self, statement, statement_vals):
        statement_vals.\
            update({
                    'date': statement.get('date'),
                    'name': statement.get('name') or False,
                    })
        return statement_vals

    @api.multi
    def file_parsing(self):
        account_period_obj = self.env['account.period']
        bank_statement_obj = bkst_list = self.env['account.bank.statement']
        seq_obj = self.env['ir.sequence']
        for wizard in self:
            encoding = wizard.encoding == 'other' and \
                wizard.encoding_other or wizard.encoding or 'utf-8'
            try:
                recordlist1 = base64.\
                    decodestring(wizard.file_data).\
                    decode(encoding).encode('utf-8')
                recordlist1 = re.split('\n'+'(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))',recordlist1)
            except:
                recordlist1 = base64.\
                    decodestring(wizard.file_data).\
                    decode(encoding, errors='replace').\
                    encode('utf-8')
                recordlist1 = re.split('\n'+'(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))',recordlist1)
            if(recordlist1[-1] == ''):
                recordlist1.pop()
            recordlist = [to_unicode(x) for x in recordlist1]
            default_journal = wizard.journal_id
            default_period = account_period_obj.with_context(account_period_prefer_normal = True).find()[0]

            err_log = _("Errors:") + "\n------\n"
            nb_err = 0
            str_log1 = _("The bank statement file has been imported") + "\n"

            bank_statements = wizard.get_file(recordlist)
            statement_update = wizard.statement_update
            fill_accounts = wizard.fill_accounts
            bank_statements = sorted(bank_statements,
                                     key=lambda statement: statement['date'])
            for statement in bank_statements:
                journal = statement.get('journal') or default_journal
                statement_period = statement.get('period_id') or \
                    self.env['account.period']
                try:       
                    """If the month already exist
                    we update the statement
                    Section to be remove
                    if we do not want a fusion of statement anymore"""
                    if statement_update:
                        bank_sts = bank_statement_obj.search([
                            ('period_id', '=', statement_period.id),
                            ('company_id', '=', journal.company_id.id),
                            ('journal_id', '=', journal.id),
                            ], limit=1)
                        if bank_sts:
                            statement_total_amount = statement.get('total_amount') or 0
                            balance_start = bank_sts.balance_start    
                            if statement.get('balance_end_real'):
                                balance_end_real = statement.get('balance_end_real') or 0
                            else:
                                balance_end_real = bank_sts.balance_end_real + \
                                    statement_total_amount
                            bank_sts.balance_end_real = balance_end_real
                            bkst_list += bank_sts
                            str_not1 = self.\
                                _create_bank_statement_line(statement,
                                                            bank_sts,
                                                            fill_accounts)
                    
                    '''If the month does not exist we create a new statement'''
                    if not bank_statement_obj.search([
                            ('period_id', '=', statement_period.id),
                            ('company_id', '=', journal.company_id.id),
                            ('journal_id', '=', journal.id),
                            ]) or statement_update == False:
                        if not statement.get('name', False):                    
                            statement['name'] = seq_obj.\
                                next_by_code('account.bank.statement')
                        previous_bank_statements = bank_statement_obj.\
                            search([('journal_id', '=', journal.id)],
                                   order='date desc, period_id desc',
                                   limit=1)
                        if previous_bank_statements:
                            balance_start = previous_bank_statements.balance_end_real
                        else:
                            balance_start = 0
                        statement_total_amount = statement.get('total_amount') or 0
                        balance_end_real = balance_start + statement_total_amount
                        period = statement_period or default_period
                        statement_vals = {
                                          'journal_id': journal.id,
                                          'balance_start': balance_start,
                                          'balance_end_real': balance_end_real,
                                          'state': 'draft',
                                          'period_id': period.id,
                                          }
                        statement_vals = self.\
                            _get_statement_vals(statement, statement_vals)
                        bk_st = bank_statement_obj.create(statement_vals)
                        bkst_list += bk_st
                        str_not1 = self.\
                            _create_bank_statement_line(statement, bk_st,
                                                        fill_accounts)
                except exceptions.except_orm, e:
                    self._cr.rollback()
                    nb_err += 1
                    err_log += '\n' + _('Application Error:') + ' ' + to_unicode(str(e))
                except Exception, e:
                    self._cr.rollback()
                    nb_err += 1
                    err_log += '\n' + _('System Error:') + ' ' + to_unicode(str(e))
                except:
                    self._cr.rollback()
                    nb_err+=1
                    err_log += '\n' + _('Unknown Error')
                    raise
        sumup_log = '\n' + _('Sum up:') + '\n' + \
            _('Number of statements:') + ' ' \
            + str(len(bkst_list)) + '\n' + \
            _('Number of error:') + ' ' + str(nb_err)
        
        total_log = str_log1 + err_log + sumup_log
        self.write({'note': total_log})
        context = self._context.copy()
        context.update({'statement_ids': bkst_list.ids})
        view = self.env.\
            ref('account_bank_statement_import.account_bank_statement_file_report_view')
        return {
            'name': _('Result'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement.import',
            'view_id': view.id,
            'target': 'new',
            'views': [(view.id, 'form')],
            'context': context,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def open_bank_statements(self):
        mod_obj = self.pool.get('ir.model.data')
        action = self.env.\
            ref('account_bank_statement_import.action_bank_statement_imported')
        action_obj = self.env['ir.actions.act_window']
        action = action.read()[0]
        context = self._context
        if context and context.get('statement_ids'):
            statements = context.get('statement_ids')
            action['domain'] = [('id','in', statements)]
        return action

    @api.model
    def _group_by_month(self, recordlist, separator=',',
                        date_format='%Y-%m-%d', date_column=0):
        month_statement = {}
        for line in recordlist:
            line_splited = re.split(separator+'(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))',line)
            try:
                date = line_splited[date_column]
                line_period = get_key_from_date(date, date_format)
                month_statement.setdefault(line_period, [])
                month_statement[line_period].append(line)
            except:
                continue
        return month_statement

    @api.model
    def check_line_uniqueness(self, name, date, amount, ref=None, journal=None):
        """
        This method checks of uniqueness of a field in the database
        """
        line_obj = self.env['account.bank.statement.line']
        domain = [
                  ('name', '=', name),
                  ('date', '=', date),
                  ('amount', '=', amount),
                  ]
        if ref:
            domain += [('ref', '=', ref)]
        if journal:
            domain += [('journal_id', '=', journal.id)]
        return line_obj.search(domain, count=True)

    @api.model
    def format_line_from_data(self, line_splited, name, date, date_val,
                              debit, credit, ref, extra_note, date_format):
        line = {}
        line['name'] = (name or name == 0) and line_splited[name] or ''
        line['date'] = ((date or date == 0) and line_splited[date]) and \
            str2date(line_splited[date], date_format) or ''
        line['date_val'] = ((date_val or date_val == 0) and \
            line_splited[date_val]) and \
            str2date(line_splited[date_val], date_format) or ''
        line['debit'] = (debit or debit == 0) and line_splited[debit] or ''
        line['credit'] = (credit or credit == 0) and line_splited[credit] or ''
        line['ref'] = (ref or ref == 0) and line_splited[ref] or ''
        line['extra_note'] = (extra_note or extra_note == 0) and \
            line_splited[extra_note] or ''
        return line

    @api.model
    def _find_journal_from_lines(self, lines, separator, ignored_lines=0):
        journal_obj = self.env['account.journal']
        journals = journal_obj.search([('import_key', '!=', False)])
        for line in lines[0:ignored_lines]:
            line_splited = re.split(separator+'(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))',line)
            for val in line_splited:
                clean_val =  val.replace('\r', '').replace('\n', '')
                journal = journal_obj.search([('import_key', '=', clean_val)])
                if journal:
                    return journal
        return self.env['account.journal']

    @api.model
    def _group_by_journal(self, recordlist, separator, date_format,
                          many_journals, many_statements, date_column,
                          ignored_lines=0, default_key=False,
                          default_journal=False):
        journal_statement = {}
        month_statement = {}
        journal_list = []
        if not many_journals:
            journal_list = [(default_journal, recordlist)]
        else:
            i = 1
            while recordlist:
                journal_lines = recordlist[0:ignored_lines]
                recordlist = recordlist[ignored_lines:]
                for line in recordlist:
                    line_splited = re.split(separator+'(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))',line)
                    add_line = False
                    for splited in line_splited:
                        if splited:
                            add_line = True
                    if add_line and line_splited == 1:
                        add_line = False
                    if add_line and line_splited[0] == '\r':
                        add_line = False
                    if add_line:
                        journal_lines.append(line)
                        recordlist = recordlist[1:]
                    else:
                        if journal_lines:
                            journal_list.append((i, journal_lines))
                            i += 1
                            break
            if journal_lines:
                journal_list.append((i, journal_lines))
        for journal, lines in journal_list:
            if not isinstance(journal, bool) and many_journals:
                journal = self._find_journal_from_lines(lines,
                                                        separator,
                                                        ignored_lines)
            month_statement = {}
            if len(lines) > ignored_lines:
                if many_statements:
                    month_statement = self.\
                        _group_by_month(lines[ignored_lines:],
                                        separator=separator,
                                        date_format=date_format,
                                        date_column=date_column)
                else:
                    month_statement = {default_key: lines[ignored_lines:]}
            if journal in journal_statement.keys():
                
                month_statement.update(journal_statement.get(journal))
            journal_statement[journal] = month_statement
        return journal_statement

    @api.model
    def format_statement_from_data(self, recordlist, separator, date_format,
                                   many_statements, many_journals,
                                   ignored_lines=0, name=False, date=False,
                                   date_val=False, debit=False, credit=False,
                                   separated_amount=False, receivable_id=False,
                                   payable_id=False, ref=False, extra_note=False,
                                   default_key=False, statement_date=False,
                                   thousand_separator=False, text_separator=False,
                                   default_journal=False):
        account_period_obj = self.env['account.period']
        bank_statements = []
        pointor = 0
        journal_statement = self.\
            _group_by_journal(recordlist, separator, date_format,
                              many_journals, many_statements, date_column=date,
                              ignored_lines=ignored_lines,
                              default_key=default_key,
                              default_journal=default_journal)
        # loop on each journals
        for journal in journal_statement.keys():
            month_statement = journal_statement.get(journal)
            # loop on each month
            for key in month_statement.keys():
                total_amount = 0
                bank_statement = {}
                bank_statement_lines = {}
                bank_statement['journal'] = journal
                bank_statement["bank_statement_line"] = {}
                 # Loop on all line of a month
                for line in month_statement[key]:
                    line_splited = re.split(separator+'(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))',line)
                    st_line = self.\
                        format_line_from_data(line_splited, name=name, date=date,
                                              date_val=date_val,
                                              debit=debit, credit=credit,
                                              ref=ref, extra_note=extra_note,
                                              date_format=date_format)
                    amount = 0
                    val_debit = st_line.pop('debit')
                    val_credit = st_line.pop('credit')
                    if text_separator:
                        st_line['name'] = st_line['name'].replace(text_separator, "")
                        st_line['ref'] = st_line['ref'].replace(text_separator, "")
                        st_line['extra_note'] = st_line['extra_note'].replace(text_separator, "")
                    if thousand_separator:
                        val_debit = val_debit.replace(thousand_separator, "")
                        val_credit = val_credit.replace(thousand_separator, "")
                    if separated_amount:
                        if val_debit:
                            st_line['account_id'] = payable_id
                            amount = str2float(val_debit, ',') or 0.0
                            if amount > 0.0:
                                amount = - amount
                        if amount == 0 and val_credit:
                            st_line['account_id'] = receivable_id
                            amount = str2float(val_credit, ',') or 0.0
                    else:
                        amount = str2float(val_debit or val_credit, ',') or 0.0
                        if amount < 0:
                            st_line['account_id'] = payable_id
                        else:
                            st_line['account_id'] = receivable_id
                    st_line['amount'] = amount
                    if self.check_line_uniqueness(st_line['name'],
                                                  st_line['date'],
                                                  st_line['amount'],
                                                  journal=journal):
                        continue
                    else:
                        bank_statement_lines[pointor] = st_line
                    bank_statement["bank_statement_line"] = bank_statement_lines
                    pointor += 1
                    total_amount += amount
                # Saving data at month level
                bank_statement["total_amount"] = total_amount
                bank_statement['date'] = statement_date or key + '-01'
                statement_date_search = bank_statement['date']
                period = account_period_obj.\
                    search([
                            ('date_start', '<=', statement_date_search),
                            ('date_stop', '>=', statement_date_search),
                            ('special', '=', False),
                            ('company_id', '=', journal.company_id.id),
                            ], limit=1)
                bank_statement['period_id'] = period
                bank_statements.append(bank_statement)
        return bank_statements

    @api.multi
    def get_separator(self):
        separator = self.separator
        if separator == 'other':
            separator = self.separator_other
        else:
            separator = SEPARATOR.get(separator, False)
        return separator or ','

    @api.model
    def get_column_number(self, value, default=False):
        value = value and value - 1
        if isinstance(value, bool):
            value = default
        return value
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
