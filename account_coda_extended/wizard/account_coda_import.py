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

from osv import fields, osv
from tools.translate import _

def str2date(date_str):
    return time.strftime("%y/%m/%d", time.strptime(date_str, "%d%m%y"))

def str2float(str):
    try:
        return float(str)
    except:
        return 0.0

def list2float(lst):
    try:
        return str2float((lambda s: s[:-3] + '.' + s[-3:])(lst))
    except:
        return 0.0

class account_coda_import(osv.osv_memory):
    _inherit = 'account.coda.import'

    def _default_journal_id(self, cr, uid, context):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, context=context)
        if company_id:
            company = company_obj.browse(cr, uid, company_id)
            if company and company.bank_journalid:
                return company.bank_journalid.id
        return False
    
    def _default_def_payable(self, cr, uid, context):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, context=context)
        if company_id:
            company = company_obj.browse(cr, uid, company_id)
            if company and company.def_payable:
                return company.def_payable.id
        return False
    
    def _default_def_receivable(self, cr, uid, context):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, context=context)
        if company_id:
            company = company_obj.browse(cr, uid, company_id)
            if company and company.def_receivable:
                return company.def_receivable.id
        return False
    
    def _default_filter_id(self, cr, uid, context):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, context=context)
        if company_id:
            company = company_obj.browse(cr, uid, company_id)
            if company and company.filter_id:
                return company.filter_id.id
        return False


    _columns = {
        'journal_id': fields.many2one('account.journal', 'Bank Journal', required=True),
        'def_payable': fields.many2one('account.account', 'Default Payable Account', domain=[('type', '=', 'payable')], required=True, help= 'Set here the payable account that will be used, by default, if the partner is not found'),
        'def_receivable': fields.many2one('account.account', 'Default Receivable Account', domain=[('type', '=', 'receivable')], required=True, help= 'Set here the receivable account that will be used, by default, if the partner is not found',),
        'awaiting_account': fields.many2one('account.account', 'Default Account for Unrecognized Movement', domain=[('type', '=', 'liquidity')], required=True, help= 'Set here the default account that will be used, if the partner is found but does not have the bank account, or if he is domiciled'),
        'filter_id': fields.many2one('account.bankimport.filters', 'Filter', required=True),
        'statement_update': fields.boolean('Update Statement'),
        'date_format': fields.char('Date Format', size=32, required=True),
    }
    
    _defaults = {
        'journal_id': lambda x, y, z, c: x._default_journal_id(y, z, c),
        'def_payable' : lambda x, y, z, c: x._default_def_payable(y, z, c),
        'def_receivable': lambda x, y, z, c: x._default_def_receivable(y, z, c),
        'filter_id' : lambda x, y, z, c: x._default_filter_id(y, z, c),
        'statement_update': False,
        'date_format': '%d/%m/%Y',
    }
    
    def get_file(self, cr, uid, ids, recordlist, filter_id, data, context):
        # based on the filter we parse the document
        filter_name = self.pool.get('account.bankimport.filters').browse(cr, uid, filter_id).name
        
#        filterObject = 'account.bankimport.filter.' + filter_name
#        bank_data = self.pool.get( filterObject )
        
        exec "from filters import " + filter_name + " as parser"
        # opening the file speficied as bank_file and read the data
        try:
            bank_statements = parser.get_data(self, cr, uid, ids, recordlist, data) # parse the data through the filter
        except IOError:
            raise
        return bank_statements
    
    def get_line_vals(self, cr, uid, line, bk_st_id, voucher_id, str_not1, context=None):
        return {
            'name': line['name'],
            'date': line['date'],
            'amount': line['amount'],
            'account_id':line['account_id'],
            'statement_id': bk_st_id,
            'voucher_id': voucher_id,
            'note': str_not1 + '\n' + line['extra_note'],
            'ref':line['ref'],
        }

    def coda_parsing(self, cr, uid, ids, context=None):

        journal_obj=self.pool.get('account.journal')
        account_period_obj = self.pool.get('account.period')
        bank_statement_obj = self.pool.get('account.bank.statement')
        bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        account_coda_obj = self.pool.get('account.coda')
        mod_obj = self.pool.get('ir.model.data')
        line_obj = self.pool.get('account.move.line')

        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]

        codafile = data['coda_data']
        journal_id = data['journal_id'][0]
        journal_code = journal_obj.browse(cr, uid, journal_id, context=context).code

        period = account_period_obj.find(cr, uid, context=context)[0]
        def_pay_acc = data['def_payable']
        def_rec_acc = data['def_receivable']
        filter_id = data['filter_id'][0]

        err_log = "Errors:\n------\n"
        nb_err=0
        std_log=''
        str_log1 = "Coda File is Imported:  "
        str_not=''
        str_not1=''

        bank_statements = []
        bank_statement = {}
        recordlist = base64.decodestring(unicode(codafile, 'utf-8')).split('\n')
        recordlist.pop()
        
        bank_statements = self.get_file(cr, uid, ids, recordlist, filter_id, data, context)
        statement_update = data['statement_update']
        #end for
        bkst_list=[]
        for statement in bank_statements:
            try:       
                '''If the month already exist we update the statement''' 
                '''Section to be remove if we do not want a fusion of statement anymore'''                                            
                for bank_statement_id in bank_statement_obj.search(cr,uid,[('period_id','=',statement.get('period_id',False))]):
                    if statement_update:
                        bk_st_id = bank_statement_id
                        statement_total_amount = statement.get('total_amount') or 0
                        balance_start = bank_statement_obj.browse(cr, uid, bk_st_id, context=context).balance_start                    
                        balance_end_real = bank_statement_obj.browse(cr, uid, bk_st_id, context=context).balance_end_real + statement_total_amount
                        bank_statement_obj.write(cr, uid, [bk_st_id], {'balance_end_real': balance_end_real}, context)
                        lines = statement.get('bank_statement_line',False)
                        if lines:
                            for value in lines:
                                journal = statement.get('journal_id',journal_id)
                                journal = journal_obj.browse(cr, uid, journal, context=context)
                                line = lines[value]
                                if not line['partner_id']:
                                    line['partner_id'] = journal.company_id.partner_id.id
                                voucher_id = False
                                rec_id = False
                                if line.get('toreconcile',False): # Fix me
                                    name = line['name'][:3] + '/' + line['name'][3:7] + '/' + line['name'][7:]
                                    rec_id = self.pool.get('account.move.line').search(cr, uid, [('name', '=', name), ('reconcile_id', '=', False), ('account_id.reconcile', '=', True)])
                                    if rec_id:
                                        result = voucher_obj.onchange_partner_id(cr, uid, [], partner_id=line['partner_id'], journal_id=statement['journal_id'], price=abs(line['amount']), currency_id = journal.company_id.currency_id.id, ttype=(line['amount'] < 0 and 'payment' or 'receipt'), context=context)
                                        voucher_res = { 'type':(line['amount'] < 0 and 'payment' or 'receipt'),
                                        'name': line['name'],#line.name,
                                        'journal_id': journal.id, #statement.journal_id.id,
                                        'account_id': result.get('account_id', journal.default_credit_account_id.id),#line.account_id.id,
                                        'company_id': journal.company_id.id,#statement.company_id.id,
                                        'currency_id': journal.company_id.currency_id.id,#statement.currency.id,
                                        'date': line['date'], #line.date,
                                        'amount':abs(line['amount']),
                                        'period_id':statement.get('period_id',False) or period,# statement.period_id.id
                                        }
                                        voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)
                                        context.update({'move_line_ids': rec_id})
                                        voucher_line_dict =  False
                                        if result['value']['line_ids']:
                                            for line_dict in result['value']['line_ids']:
                                                move_line = line_obj.browse(cr, uid, line_dict['move_line_id'], context)
                                                if line.move_id.id == move_line.move_id.id:
                                                    voucher_line_dict = line_dict
        
                                        if voucher_line_dict:
                                            voucher_line_dict.update({'voucher_id':voucher_id})
                                            voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
        
                                        mv = self.pool.get('account.move.line').browse(cr, uid, rec_id[0], context=context)
                                        if mv.partner_id:
                                            line['partner_id'] = mv.partner_id.id
                                            if line['amount'] < 0:
                                                line['account_id'] = mv.partner_id.property_account_payable.id
                                            else:
                                                line['account_id'] = mv.partner_id.property_account_receivable.id
                                str_not1 = ''
                                if line.has_key('contry_name') and line.has_key('cntry_number'):
                                    str_not1="Partner name:%s \n Partner Account Number:%s \n Communication:%s \n Value Date:%s \n Entry Date:%s \n"%(line["contry_name"], line["cntry_number"], line["free_comm"]+line['extra_note'], line["val_date"][0], line["entry_date"][0])

                                bank_statement_line_obj.create(cr, uid, {
                                           'name':line['name'],
                                           'date': line['date'],
                                           'amount': line['amount'],
                                           'account_id':line['account_id'],
                                           'statement_id': bk_st_id,
                                           'voucher_id': voucher_id,
                                           'note': str_not1 + '\n' + line['extra_note'],
                                           'ref':line['ref'],
                                           })
                        bkst_list.append(bk_st_id)                   
                
                '''If the month does not exist we create a new statement'''       
                if not bank_statement_obj.search(cr,uid,[('period_id','=',statement.get('period_id',False))]) or statement_update == False:
                    if not statement.get('name',False):                    
                        statement['name'] = self.pool.get('ir.sequence').next_by_code(cr, uid, 'account.bank.statement')
                    previous_bank_statement_id = bank_statement_obj.search(cr, uid, [], order=('date desc,period_id desc'), context=context)
                    if previous_bank_statement_id:
                        balance_start = bank_statement_obj.browse(cr, uid, previous_bank_statement_id[0], context=context).balance_end_real 
                    else:
                        balance_start = 0
#                        err_log += '\n Should Not Append'
#                        raise
                    journal = statement.get('journal_id',journal_id)
                    statement_total_amount = statement.get('total_amount') or 0
                    balance_end_real = balance_start + statement_total_amount
                    bk_st_id = bank_statement_obj.create(cr, uid, {
                        'journal_id': journal,
                        'date': time.strftime('%Y-%m-%d', time.strptime(statement.get('date',time.strftime('%Y/%m/%d')), "%Y/%m/%d")),
                        'period_id': statement.get('period_id',False) or period,
                        'balance_start': balance_start,
                        'balance_end_real': balance_end_real,
                        'state': 'draft',
                        'name': statement.get('name',False),
                    })
                
                    lines = statement.get('bank_statement_line',False)
                    if lines:
                        for value in lines:
                            journal = journal_obj.browse(cr, uid, journal, context=context)
                            line = lines[value]
                            if not line['partner_id']:
                                line['partner_id'] = journal.company_id and journal.company_id.partner_id.id or False
                            voucher_id = False
                            rec_id = False
                            if line.get('toreconcile',False): # Fix me
                                name = line['name'][:3] + '/' + line['name'][3:7] + '/' + line['name'][7:]
                                rec_id = self.pool.get('account.move.line').search(cr, uid, [('name', '=', name), ('reconcile_id', '=', False), ('account_id.reconcile', '=', True)])
                                if rec_id:
                                    result = voucher_obj.onchange_partner_id(cr, uid, [], partner_id=line['partner_id'], journal_id=statement['journal_id'], price=abs(line['amount']), currency_id = journal.company_id.currency_id.id, ttype=(line['amount'] < 0 and 'payment' or 'receipt'), context=context)
                                    voucher_res = { 'type':(line['amount'] < 0 and 'payment' or 'receipt'),
                                    'name': line['name'],#line.name,
#                                    'partner_id': line['partner_id'],#line.partner_id.id,
                                    'journal_id': journal.id, #statement.journal_id.id,
                                    'account_id': result.get('account_id', journal.default_credit_account_id.id),#line.account_id.id,
                                    'company_id': journal.company_id.id,#statement.company_id.id,
                                    'currency_id': journal.company_id.currency_id.id,#statement.currency.id,
                                    'date': line['date'], #line.date,
                                    'amount':abs(line['amount']),
                                    'period_id':statement.get('period_id',False) or period,# statement.period_id.id
                                    }
                                    voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)
                                    context.update({'move_line_ids': rec_id})
    
                                    voucher_line_dict =  False
                                    if result['value']['line_ids']:
                                        for line_dict in result['value']['line_ids']:
                                            move_line = line_obj.browse(cr, uid, line_dict['move_line_id'], context)
                                            if line.move_id.id == move_line.move_id.id:
                                                voucher_line_dict = line_dict
    
                                    if voucher_line_dict:
                                        voucher_line_dict.update({'voucher_id':voucher_id})
                                        voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
    
            #                            reconcile_id = statement_reconcile_obj.create(cr, uid, {
            #                                'line_ids': [(6, 0, rec_id)]
            #                                }, context=context)
            #
    
                                    mv = self.pool.get('account.move.line').browse(cr, uid, rec_id[0], context=context)
                                    if mv.partner_id:
                                        line['partner_id'] = mv.partner_id.id
                                        if line['amount'] < 0:
                                            line['account_id'] = mv.partner_id.property_account_payable.id
                                        else:
                                            line['account_id'] = mv.partner_id.property_account_receivable.id
                            str_not1 = ''
                            if line.has_key('contry_name') and line.has_key('cntry_number'):
                                str_not1="Partner name:%s \n Partner Account Number:%s \n Communication:%s \n Value Date:%s \n Entry Date:%s \n"%(line["contry_name"], line["cntry_number"], line["free_comm"]+line['extra_note'], line["val_date"][0], line["entry_date"][0])
                            
                            line_vals = self.get_line_vals(cr, uid, line, bk_st_id, voucher_id, str_not1, context=context)
                            bank_statement_line_obj.create(cr, uid, line_vals, context=context)
    
                    bkst_list.append(bk_st_id)

            except osv.except_osv, e:
                cr.rollback()
                nb_err += 1
                err_log += '\n Application Error: ' + str(e)
                raise # REMOVEME

            except Exception, e:
                cr.rollback()
                nb_err += 1
                err_log += '\n System Error: '+str(e)
                raise # REMOVEME
            except:
                cr.rollback()
                nb_err+=1
                err_log += '\n Unknown Error'
                raise
        err_log += '\n\nNumber of statements: '+ str(len(bkst_list))
        err_log += '\nNumber of error:'+ str(nb_err) +'\n'
        test = mod_obj.browse(cr, uid,filter_id, context=context)
        account_coda_obj.create(cr, uid, {
            'name': 'test',
            'coda_data': codafile,
            'bank_statement_ids': [(6, 0, bkst_list,)],
            'note': str_log1+str_not+std_log+err_log,
            'date': time.strftime("%Y-%m-%d"),
            'coda_creation_date': time.strftime("%Y-%m-%d"),
            'user_id': uid,
        })
        
        test = ''
        test = str_log1 + std_log + err_log
        self.write(cr, uid, ids, {'note': test}, context=context)
        context.update({ 'statment_ids': bkst_list})
        model_data_ids = mod_obj.search(cr, uid, [('model', '=', 'ir.ui.view'), ('name', '=', 'view_bank_statement_tree')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']

        return {
            'name': _('Result'),
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.coda.import',
            'view_id': False,
            'target': 'new',
            'views': [(resource_id, 'tree')],
            'context': context,
            'type': 'ir.actions.act_window',
        }
        
account_coda_import()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: