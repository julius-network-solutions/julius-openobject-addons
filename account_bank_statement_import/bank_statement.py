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

COLUMNS = [
           (1, 'A'),
           (2, 'B'),
           (3, 'C'),
           (4, 'D'),
           (5, 'E'),
           (6, 'F'),
           (7, 'G'),
           (8, 'H'),
           (9, 'I'),
           (10, 'J'),
           (11, 'K'),
           (12, 'L'),
           (13, 'M'),
           (14, 'N'),
           (15, 'O'),
           (16, 'P'),
           (17, 'Q'),
           (18, 'R'),
           (19, 'S'),
           (20, 'T'),
           (21, 'U'),
           (22, 'V'),
           (23, 'W'),
           (24, 'X'),
           (25, 'Y'),
           (26, 'Z'),
           ]

SEPARATOR = {'comma': ',', 'semicolon': ';', 'tab': '\t', 'space': ' ', 'pipe': '|'}

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