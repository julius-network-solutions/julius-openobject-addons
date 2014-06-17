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

import time
import base64

from openerp.osv import fields, orm
from openerp.tools.translate import _

class account_bank_statement_import(orm.TransientModel):
    _name = "account.bank.statement.import"
    _description = "Bank statement import"

    def _default_journal_id(self, cr, uid, context=None):
        """ This method will return the default value
        for the journal from the definition
        of the filter or of the company."""
        if context is None: context = {}
        company_obj = self.pool.get('res.company')
        company_id = company_obj.\
            _company_default_get(cr, uid, context=context)
        res = False
        if company_id:
            company = company_obj.browse(cr, uid, company_id, context=context)
            if company.def_filter_id and \
                company.def_filter_id.def_bank_journal_id:
                res = company.def_filter_id.def_bank_journal_id.id
            if not res and company.def_bank_journal_id:
                return company.def_bank_journal_id.id
        return res
    
    def _default_def_payable(self, cr, uid, context=None):
        """ This method will return the default value
        for the payable account from the definition
        of the filter or of the company."""
        if context is None: context = {}
        company_obj = self.pool.get('res.company')
        company_id = company_obj.\
            _company_default_get(cr, uid, context=context)
        res = False
        if company_id:
            company = company_obj.browse(cr, uid, company_id, context=context)
            if company.def_filter_id and \
                company.def_filter_id.def_payable_id:
                res = company.def_filter_id.def_payable_id.id
            if not res and company.def_payable_id:
                return company.def_payable_id.id
        return res
    
    def _default_def_receivable(self, cr, uid, context=None):
        """ This method will return the default value 
        for the receivable account from the definition
        of the filter or of the company."""
        if context is None: context = {}
        company_obj = self.pool.get('res.company')
        company_id = company_obj.\
            _company_default_get(cr, uid, context=context)
        res = False
        if company_id:
            company = company_obj.browse(cr, uid, company_id, context=context)
            if company.def_filter_id and \
                company.def_filter_id.def_receivable_id:
                res = company.def_filter_id.def_receivable_id.id
            if not res and company.def_receivable_id:
                return company.def_receivable_id.id
        return res
    
    def _default_def_awaiting(self, cr, uid, context=None):
        """ This method will return the default value 
        for the awaiting account from the definition
        of the filter or of the company."""
        if context is None: context = {}
        company_obj = self.pool.get('res.company')
        company_id = company_obj.\
            _company_default_get(cr, uid, context=context)
        res = False
        if company_id:
            company = company_obj.browse(cr, uid, company_id, context=context)
            if company.def_filter_id and \
                company.def_filter_id.def_awaiting_id:
                res = company.def_filter_id.def_awaiting_id.id
            if not res and company.def_awaiting_id:
                return company.def_awaiting_id.id
        return res
    
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
    
    def _default_date_format(self, cr, uid, context=None):
        """ This method will return the default value 
        for the date format from the definition
        of the filter or of the company."""
        if context is None: context = {}
        company_obj = self.pool.get('res.company')
        company_id = company_obj.\
            _company_default_get(cr, uid, context=context)
        res = False
        if company_id:
            company = company_obj.browse(cr, uid, company_id, context=context)
            if company.def_filter_id and \
                company.def_filter_id.def_date_format:
                res = company.def_filter_id.def_date_format
            if not res and company.def_date_format:
                res = company.def_date_format
        return res or '%d/%m/%Y'

    _columns = {
        'journal_id': fields.many2one('account.journal',
                                      'Bank Journal',
                                      required=True),
        'payable_id': fields.many2one('account.account',
            'Payable Account', domain=[('type', '=', 'payable')],
            required=True,
            help="Set here the payable account that will be used "\
            "by default, if the partner is not found"),
        'receivable_id': fields.many2one('account.account',
            'Receivable Account', domain=[('type', '=', 'receivable')],
            required=True,
            help="Set here the receivable account that will be used "\
            "by default, if the partner is not found",),
        'awaiting_id': fields.many2one('account.account',
            'Account for Unrecognized Movement',
            domain=[('type', '=', 'liquidity')],
            required=True,
            help="Set here the default account that will be used "\
            "if the partner is found but does not have the bank account, "\
            "or if he is domiciled",),
        'filter_id': fields.many2one('account.bankimport.filters',
                                     'Filter', required=True),
        'statement_update': fields.boolean('Update Statement'),
        'date_format': fields.char('Date Format', size=32, required=True),
        'file_data': fields.binary('File to import', required=True),
        'file_fname': fields.char('Filename', size=128, required=True),
        'note': fields.text('Log'),
    }
    
    _defaults = {
        'journal_id': lambda self, cr, uid, context:
            self._default_journal_id(cr, uid, context),
        'payable_id': lambda self, cr, uid, context:
            self._default_def_payable(cr, uid, context),
        'receivable_id': lambda self, cr, uid, context:
            self._default_def_receivable(cr, uid, context),
        'awaiting_id': lambda self, cr, uid, context:
            self._default_def_awaiting(cr, uid, context),
        'filter_id': lambda self, cr, uid, context:
            self._default_filter_id(cr, uid, context),
        'date_format': lambda self, cr, uid, context:
            self._default_date_format(cr, uid, context),
        'file_fname': '',
        'statement_update': False,
    }
    
    def get_file(self, cr, uid, ids, recordlist, filter_id, data, context):
        # based on the filter we parse the document
        filter_obj = self.pool.get('account.bankimport.filters')
        filter_name = filter_obj.browse(cr, uid, filter_id).filter
        
        exec "from filters import " + filter_name + " as parser"
        # opening the file speficied as bank_file and read the data
        try:
            # parse the data through the filter
            bank_statements = parser.\
                get_data(self, cr, uid, ids, recordlist, data)
        except IOError:
            raise
        return bank_statements

    def onchange_filter_id(self, cr, uid, ids, filter_id, context=None):
        if context is None: context = {}
        res = {'value': {}}
        # update related fields
        if filter_id:
            filter_obj = self.pool.get('account.bankimport.filters')
            filter = filter_obj.browse(cr, uid, filter_id, context=None)
            value = {}
            if filter.def_bank_journal_id:
                value.update({
                    'journal_id': filter.def_bank_journal_id.id,
                })
            if filter.def_payable_id:
                value.update({
                    'payable_id': filter.def_payable_id.id,
                })
            if filter.def_receivable_id:
                value.update({
                    'receivable_id': filter.def_receivable_id.id,
                })
            if filter.def_awaiting_id:
                value.update({
                    'awaiting_id': filter.def_awaiting_id.id,
                })
            if filter.def_date_format:
                value.update({
                    'date_format': filter.def_date_format,
                })
            res['value'] = value
        return res

    def _get_line_vals(self, cr, uid, line,
                       bk_st_id, voucher_id,
                       str_not1, context=None):
        return {
            'name': line.get('name') or '',
            'date': line.get('date') or False,
            'amount': line.get('amount') or 0,
            'account_id': line.get('account_id') or False,
            'partner_id': line.get('partner_id') or False,
            'statement_id': bk_st_id,
            'voucher_id': voucher_id,
            'note': (str_not1 and (str_not1 + '\n') or '') + line.get('extra_note', ''),
            'ref': line.get('ref') or '',
        }

    def _voucher_create(self, cr, uid, statement,
                        line, journal, context=None):
        if context == None:
            context = {}
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        line_obj = self.pool.get('account.move.line')
        
        name = line['name'][:3] + '/' + \
            line['name'][3:7] + '/' + line['name'][7:]
        rec_ids = line_obj.search(cr, uid, [
            ('name', '=', name),
            ('reconcile_id', '=', False),
            ('account_id.reconcile', '=', True)
        ], limit=1, context=context)
        if rec_ids:
            result = voucher_obj.onchange_partner_id(cr, uid, [],
                partner_id=line['partner_id'],
                journal_id=statement['journal_id'],
                price=abs(line['amount']),
                currency_id =journal.company_id.currency_id.id,
                ttype=(line['amount'] < 0 and 'payment' or 'receipt'),
                context=context)
            voucher_res = {
                'type': ((line.get('amount') or 0) < 0 and \
                         'payment' or 'receipt'),
                'name': line.get('name') or '',
                'journal_id': journal.id,
                'account_id': result.get('value') and \
                    result['value'].get('account_id') or \
                    journal.default_credit_account_id.id,
                'company_id': journal.company_id.id,
                'currency_id': journal.company_id.currency_id.id,
                'date': line.get('date') or False,
                'amount': abs(line.get('amount') or 0),
                'period_id': statement.get('period_id') or period,
            }
            voucher_id = voucher_obj.\
                create(cr, uid, voucher_res, context=context)
            context.update({'move_line_ids': rec_ids})
            voucher_line_dict =  False
            if result['value']['line_ids']:
                for line_dict in result['value']['line_ids']:
                    move_line = line_obj.\
                        browse(cr, uid, line_dict['move_line_id'], context)
                    if line.move_id.id == move_line.move_id.id:
                        voucher_line_dict = line_dict

            if voucher_line_dict:
                voucher_line_dict.update({'voucher_id': voucher_id})
                line_id = voucher_line_obj.\
                    create(cr, uid, voucher_line_dict, context=context)
            mv = line_obj.browse(cr, uid, rec_ids[0], context=context)
            if mv.partner_id:
                line['partner_id'] = mv.partner_id.id
                if line['amount'] < 0:
                    line['account_id'] = mv.partner_id.\
                        property_account_payable.id
                else:
                    line['account_id'] = mv.partner_id.\
                        property_account_receivable.id
        return voucher_id, line

    def _create_bank_statement_line(self, cr, uid,
                                    statement, journal,
                                    bk_st_id, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('account.bank.statement.line')
        lines = statement.get('bank_statement_line') or {}
        str_not1 = ''
        for key in lines.keys():
            line = lines[key]
#            if not line['partner_id']:
#                line['partner_id'] = journal.company_id and \
#                    journal.company_id.partner_id.id or False
            voucher_id = False
            if line.get('toreconcile') or False: # Fix me
                voucher_id, line = self.\
                    _voucher_create(cr, uid, statement=statement,
                                    line=line, journal=journal,
                                    context=context)

            if line.has_key('contry_name') and line.has_key('cntry_number'):
                str_not1 += "Partner name:%s \n Partner Account Number:%s \n"\
                "Communication:%s \n Value Date:%s \n"
                "Entry Date:%s \n" %(line["contry_name"],
                                     line["cntry_number"],
                                     line["free_comm"]+line['extra_note'],
                                     line["val_date"][0],
                                     line["entry_date"][0])
            line_vals = self.\
                _get_line_vals(cr, uid, line, bk_st_id,
                               voucher_id, str_not1, context=context)
            line_id = line_obj.create(cr, uid, line_vals, context=context)
        return str_not1

    def file_parsing(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        journal_obj = self.pool.get('account.journal')
        account_period_obj = self.pool.get('account.period')
        bank_statement_obj = self.pool.get('account.bank.statement')
        mod_obj = self.pool.get('ir.model.data')
        seq_obj = self.pool.get('ir.sequence')

        data = self.read(cr, uid, ids[0],  context=context)
        
        file_data = data['file_data']
        journal_id = data['journal_id'][0]

        period = account_period_obj.find(cr, uid, context=context)[0]
#        def_pay_acc = data['payable_id']
#        def_rec_acc = data['receivable_id']
        filter_id = data['filter_id'][0]

        err_log = _("Errors:") + "\n------\n"
        nb_err = 0
        str_log1 = _("The bank statement file has been imported") + "\n"

        bank_statements = []
        bank_statement = {}
        recordlist = base64.decodestring(unicode(file_data, 'utf-8')).split('\n')
        recordlist.pop()
        
        bank_statements = self.\
            get_file(cr, uid, ids, recordlist, filter_id, data, context=context)
        statement_update = data['statement_update']
        #end for
        bkst_list = []
        for statement in bank_statements:
            statement_journal_id = statement.get('journal_id') or journal_id
            journal = journal_obj.\
                browse(cr, uid, statement_journal_id, context=context)
            try:       
                """If the month already exist
                we update the statement
                Section to be remove
                if we do not want a fusion of statement anymore"""
                if statement_update:
                    bk_st_ids = bank_statement_obj.search(cr, uid, [
                        ('period_id', '=', statement.get('period_id')),
                        ('company_id', '=', journal.company_id.id)
                        ], limit=1, context=context)
                    if bk_st_ids:
                        bk_st_id = bk_st_ids[0]
                        statement_data = bank_statement_obj.\
                            browse(cr, uid, bk_st_id, context=context)
                        statement_total_amount = statement.get('total_amount') or 0
                        balance_start = statement_data.balance_start                    
                        balance_end_real = statement_data.balance_end_real + \
                            statement_total_amount
                        bank_statement_obj.write(cr, uid, [bk_st_id], {
                                'balance_end_real': balance_end_real,
                            }, context=context)
                        bkst_list.append(bk_st_id)
                        str_not1 = self.\
                            _create_bank_statement_line(cr, uid, statement,
                                                        journal, bk_st_id,
                                                        context=context)
                
                '''If the month does not exist we create a new statement'''
                if not bank_statement_obj.search(cr, uid, [
                        ('period_id', '=', statement.get('period_id',False))
                        ], context=context) or statement_update == False:
                    if not statement.get('name',False):                    
                        statement['name'] = seq_obj.\
                            next_by_code(cr, uid, 'account.bank.statement')
                    previous_bank_statement_ids = bank_statement_obj.\
                        search(cr, uid, [],
                        order=('date desc,period_id desc'), context=context)
                    if previous_bank_statement_ids:
                        balance_start = bank_statement_obj.\
                            browse(cr, uid, previous_bank_statement_ids[0],
                                   context=context).balance_end_real
                    else:
                        balance_start = 0
                    statement_total_amount = statement.get('total_amount') or 0
                    balance_end_real = balance_start + statement_total_amount
                    bk_st_id = bank_statement_obj.create(cr, uid, {
                        'journal_id': statement_journal_id,
                        'date': statement.get('date'),
                        'period_id': statement.get('period_id') or period,
                        'balance_start': balance_start,
                        'balance_end_real': balance_end_real,
                        'state': 'draft',
                        'name': statement.get('name') or False,
                    }, context=context)
                    bkst_list.append(bk_st_id)
                    str_not1 = self.\
                        _create_bank_statement_line(cr, uid, statement,
                                                    journal, bk_st_id,
                                                    context=context)

            except orm.except_orm, e:
                cr.rollback()
                nb_err += 1
                err_log += '\n' + _('Application Error:') + ' ' + str(e)
                raise # REMOVEME

            except Exception, e:
                cr.rollback()
                nb_err += 1
                err_log += '\n' + _('System Error:') + ' ' + str(e)
                raise # REMOVEME
            except:
                cr.rollback()
                nb_err+=1
                err_log += '\n' + _('Unknown Error')
                raise
        sumup_log = '\n' + _('Sum up:') + '\n' + \
            _('Number of statements:') + ' ' \
            + str(len(bkst_list)) + '\n' + \
            _('Number of error:') + ' ' + str(nb_err)
        
        total_log = str_log1 + err_log + sumup_log
        self.write(cr, uid, ids, {'note': total_log}, context=context)
        context.update({'statement_ids': bkst_list})
        model_id, res_id = mod_obj.\
            get_object_reference(cr, uid,
                                 'account_bank_statement_import',
                                 'account_bank_statement_file_report_view')
        return {
            'name': _('Result'),
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement.import',
            'view_id': res_id,
            'target': 'new',
            'views': [(res_id, 'form')],
            'context': context,
            'type': 'ir.actions.act_window',
        }

    def open_bank_statements(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        model_id, res_id = mod_obj.\
            get_object_reference(cr, uid,
                                 'account_bank_statement_import',
                                 'action_bank_statement_imported')
        
        action_obj = self.pool.get('ir.actions.act_window')
        action = action_obj.read(cr, uid, res_id, [], context=context)
        if context and context.get('statement_ids'):
            action['domain'] = [('id', 'in', context.get('statement_ids'))]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: