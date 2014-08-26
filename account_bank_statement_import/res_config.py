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

from openerp import fields, models, api, _

class account_config_settings(models.TransientModel):
    _inherit = 'account.config.settings'

    def_bank_journal_id = fields.Many2one('account.journal',
                                          related='company_id.def_bank_journal_id',
                                          string="Default Company's Bank Journal")
    def_payable_id = fields.Many2one('account.account',
                                     related='company_id.def_payable_id',
                                     string="Default Company's Payable Account",
                                     domain=[('type','=','payable')])
    def_receivable_id = fields.Many2one('account.account',
                                        related='company_id.def_receivable_id',
                                        string="Default Company's Receivable Account",
                                        domain=[('type','=','receivable')])
    def_awaiting_id = fields.Many2one('account.account',
                                      related='company_id.def_awaiting_id',
                                      string="Default Company's Account for Unrecognized Movement",
                                      domain=[('type', '=', 'liquidity')])
    def_filter_id = fields.Many2one('account.bankimport.filters',
                                    related='company_id.def_filter_id',
                                    string="Default Company's Filter")
    def_date_format = fields.Char("Default Company's Date Format",
                                  related='company_id.def_date_format',
                                  size=32)

    @api.multi
    def open_filters_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Activate',
            'res_model': 'account.bankimport.filters',
            'view_mode': 'tree,form',
            'domain': ['|',
                       ('active', '=', True),
                       ('active', '=', False)],
            'context': {'search_default_active': 1,
                        'search_default_not_active': 1},
        }

    @api.onchange('def_filter_id')
    def onchange_filter_id(self):
        filter = self.def_filter_id
        self.def_bank_journal_id = filter.def_bank_journal_id.id
        self.def_payable_id = filter.def_payable_id.id
        self.def_receivable_id = filter.def_receivable_id.id
        self.def_awaiting_id = filter.def_awaiting_id.id
        self.def_date_format = filter.def_date_format

    @api.onchange('company_id')
    def onchange_filter_company_id(self):
        filter = self.company_id.def_filter_id
        self.def_bank_journal_id = filter.def_bank_journal_id.id
        self.def_payable_id = filter.def_payable_id.id
        self.def_receivable_id = filter.def_receivable_id.id
        self.def_awaiting_id = filter.def_awaiting_id.id
        self.def_date_format = filter.def_date_format

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
