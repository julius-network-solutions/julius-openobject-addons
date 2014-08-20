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
from openerp import fields, models, _
     
class account_bankimport_filters(models.Model):
    _name = "account.bankimport.filters"
    _description = "Define the filters, which is related to the file"

    filter = fields.Char('Filtername', size=64, required=True)
    name = fields.Char('Filename', size=128, required=True)
    active = fields.Boolean('Active')
    def_bank_journal_id = fields.Many2one('account.journal',
                                          'Default Bank Journal')
    def_payable_id = fields.Many2one('account.account',
                                           'Default Payable Account',
                                           domain=[('type','=','payable')])
    def_receivable_id = fields.Many2one('account.account',
                                        'Default Receivable Account',
                                        domain=[('type','=','receivable')])
    def_awaiting_id = fields.Many2one('account.account',
                                      'Default Account for Unrecognized Movement',
                                      domain=[('type','=','liquidity')])
    def_date_format = fields.Char('Default Date Format', size=32)

class res_company(models.Model):
    _inherit = 'res.company'

    def_bank_journal_id = fields.Many2one('account.journal',
                                          'Default Bank Journal')
    def_payable_id = fields.Many2one('account.account',
                                     'Default Payable Account',
                                     domain=[('type','=','payable')])
    def_receivable_id = fields.Many2one('account.account',
                                        'Default Receivable Account',
                                        domain=[('type','=','receivable')])
    def_awaiting_id = fields.Many2one('account.account',
                                      'Default Account for Unrecognized Movement',
                                      domain=[('type','=','liquidity')])
    def_filter_id = fields.Many2one('account.bankimport.filters',
                                    'Default Filter')
    def_date_format = fields.Char('Default Date Format', size=32)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: