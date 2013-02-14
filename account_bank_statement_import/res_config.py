# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools

class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'

    _columns = {
        'def_bank_journal_id': fields.related('company_id', 'def_bank_journal_id', type='many2one', relation='account.journal',
            string='Default Bank Journal'),
        'def_payable_id': fields.related('company_id', 'def_payable_id', type='many2one', relation='account.account',
            string='Default Payable Account', domain=[('type','=','payable')]),
        'def_receivable_id': fields.related('company_id', 'def_receivable_id', type='many2one', relation='account.account',
            string='Default Receivable Account', domain=[('type','=','receivable')]),
        'def_awaiting_id': fields.related('company_id', 'def_awaiting_id', type='many2one', relation='account.account',
            string='Default Account for Unrecognized Movement', domain=[('type', '=', 'liquidity')]),
        'def_filter_id': fields.related('company_id', 'def_filter_id', type='many2one', relation='account.bankimport.filters',
            string='Default Filter'),
        'def_date_format': fields.related('company_id', 'def_date_format', type='char', size=32,
            string='Default Date Format'),
    }

    _defaults = {}

    def open_filters_form(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Activate',
            'res_model': 'account.bankimport.filters',
            'view_mode': 'tree,form',
            'domain': ['|',('active', '=', True),('active', '=', False)],
            'context': {'search_default_active':1, 'search_default_not_active':1},
        }
        
    def onchange_company_id(self, cr, uid, ids, company_id):
        # update related fields
        res = super(account_config_settings, self).onchange_company_id(cr, uid, ids, company_id)
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id)
            res['value'].update({
                'def_bank_journal_id': company.def_bank_journal_id and company.def_bank_journal_id.id or False,
                'def_payable_id': company.def_payable_id and company.def_payable_id.id or False,
                'def_receivable_id': company.def_receivable_id and company.def_receivable_id.id or False,
                'def_awaiting_id': company.def_awaiting_id and company.def_awaiting_id.id or False,
                'def_filter_id': company.def_filter_id and company.def_filter_id.id or False,
                'def_date_format': company.def_date_format or False,
            })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
