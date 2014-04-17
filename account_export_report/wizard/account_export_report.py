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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from osv import fields, osv, orm

class account_export_report(orm.Model):
    _name = "account.export.report"
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', select=1),
        'date_form': fields.date('Start Date'),
        'date_to': fields.date('End Date'),
        'period_form_id': fields.many2one('account.period', 'Start Period'),
        'period_to_id': fields.many2one('account.period', 'End Period'),
        'child': fields.boolean('Include Childs'),
        'account_ids': fields.many2many('account.account', 'account_account_export_rel', 'account_export_id', 'account_id', 'Accounts'),
        'analytic_account_ids': fields.many2many('account.analytic.account', 'analytic_account_export_rel','account_export_id', 'analytic_account_id','Analytic Accounts'),
    }
    _defaults = {
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'res.partner', context=c),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context==None:
            context = {}
        line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        current_data = self.browse(cr, uid, ids[0], context=context)
        
        domain = []
        if current_data.date_form:
            domain += [('date','>=',current_data.date_form)]
        if current_data.date_to:
            domain += [('date','<=',current_data.date_to)]
        if current_data.period_form_id:
            domain += [('date','>=',current_data.period_form_id.date_start)]
        if current_data.period_to_id:
            domain += [('date','<=',current_data.period_to_id.date_stop)]
        if current_data.company_id:
            domain += [('company_id','=',current_data.company_id.id)]
        if current_data.account_ids:
            account_ids = []
            for account_data in current_data.account_ids:
                if current_data.child:
                    code = str(account_data.code)
                    len_code = len(code)
                    while code[len_code-1] == '0':
                        len_code -= 1
                        code = code[0:len_code] 
                    account_ids.extend(account_obj.search(cr, uid, [('code', 'ilike', code)], context=context))
                else:
                    account_ids.append(account_data.id)
                domain = [('account_id','in',account_ids)]
        if current_data.analytic_account_ids:
            analytic_ids = [x.id for x in current_data.analytic_account_ids]
            domain += [('analytic_account_id','in',analytic_ids)]
        line_ids = line_obj.search(cr, uid, domain, context=context)
        if line_ids:
            data = line_obj.read(cr, uid, line_ids[0], context=context)
            datas = {
                 'ids': line_ids,
                 'model': 'account.move.line',
                 'form': data,
                 'context': context,
            }
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.export.aeroo.report.ods',
                'datas': datas,
            }
        else:
            return True
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
