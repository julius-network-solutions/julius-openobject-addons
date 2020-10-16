# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Julius Network Solutions SARL <contact@julius.fr>
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
from ftplib import FTP
import base64
import logging
_logger = logging.getLogger(__name__)

class account_bank_statement_folder(models.Model):
    _name = 'account.bank.statement.folder'
    _description = 'Bank statement folder'

    name = fields.Char(required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    host = fields.Char(required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    port = fields.Integer(required=True, readonly=True,
                       states={'draft': [('readonly', False)]}, default=21)
    path = fields.Char(required=True, readonly=True,
                       states={'draft': [('readonly', False)]}, default='/')
    login = fields.Char(required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    password = fields.Char(required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    filter_id = fields.Many2one("account.bankimport.filters", "Filter to use",
                                required=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    state = fields.Selection([
                              ('draft', 'Draft'),
                              ('open', 'Open'),
                              ('error', 'Error'),
                              ('inactive', 'Inactive'),
                              ], default='draft', readonly=True)
    error_msg = fields.Text(readonly=True)

    @api.one
    def get_files(self):
        """
        Method which is importing files into the
        account_bank_statement_file_to_import table
        """
        def download_cb(block):
            f.write(block)
        file_obj = self.env['account.bank.statement.file.to.import']
        ftp = FTP(user=self.login, passwd=self.password)
        ftp.connect(self.host, port=self.port)
        ftp.login(user=self.login, passwd=self.password)
        ftp.cwd(self.path)
        file_names = ftp.nlst()
        file_imported = file_obj.\
            search([
                    ('name', 'in', file_names),
                    ('path', '=', self.path),
                    ('folder_id', '=', self.id),
                    ])
        for imported in file_imported:
            if imported.name in file_names:
                file_names.remove(imported.name)
        for file in file_names:
            try:
                f = open('/tmp/file.csv', "wb")
                ftp.retrbinary("RETR " + file, download_cb)
                f.close()
                binary = open('/tmp/file.csv','rb').read().encode('base64')
                vals = {
                        'name': file,
                        'path': self.path,
                        'filter_id': self.filter_id.id,
                        'folder_id': self.id,
                        'file': binary,
                        'name': file,
                        }
                file_obj.create(vals)
            except:
                _logger.warning('Error on file %s' %file)
                continue
        ftp.close()

    @api.one
    def test_connexion(self):
        """
        Method which is importing files into the
        account_bank_statement_file_to_import table
        """
        state = 'error'
        try:
            ftp = FTP(user=self.login, passwd=self.password)
            ftp.connect(self.host, port=self.port)
            ftp.login(user=self.login, passwd=self.password)
            ftp.cwd(self.path)
            ftp.close()
            state = 'open'
            self.error_msg = False
        except Exception as e:
            _logger.warning('Impossible to connect FTP: %s' %e)
            self.error_msg = e
        self.state = state

    @api.one
    def set_draft(self):
        self.state = 'draft'

    def cron_import_files(self, cr, uid, context=None):
        """
        CRON importing files into the
        account_bank_statement_file_to_import table
        """
        active_ids = self.search(cr, uid, [
                                           ('state', '=', 'open'),
                                           ], context=context)
        self.get_files(cr, uid, active_ids, context=context)

class account_bank_statement_file_to_import(models.Model):
    _name = 'account.bank.statement.file.to.import'
    _description = 'Bank statement files to import'

    name = fields.Char(readonly=True,
                       states={'draft': [('readonly', False)]})
    path = fields.Char(readonly=True,
                       states={'draft': [('readonly', False)]})
    file = fields.Binary(required=True, readonly=True,
                         states={'draft': [('readonly', False)]})
    filter_id = fields.Many2one("account.bankimport.filters", "Filter to use",
                                required=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    folder_id = fields.Many2one("account.bank.statement.folder",
                                "Folder", readonly=True,
                                states={'draft': [('readonly', False)]})
    state = fields.Selection([
                              ('draft', 'Draft'),
                              ('imported', 'Imported'),
                              ('error', 'Error'),
                              ], 'State', default='draft', readonly=True)
    error_msg = fields.Text(readonly=True)

    @api.one
    def import_files(self):
        """
        import file using the wanted filter
        """
        import_obj = self.env["account.bank.statement.import"]
        filter = self.filter_id
        vals = {
                'filter_id': self.filter_id.id,
                'file_data': self.file,
                'journal_id': self.filter_id.def_bank_journal_id.id,
                'many_journals': filter.many_journals,
                'date_format': filter.def_date_format,
                'separator': filter.separator,
                'separator_other': filter.separator_other,
                'ignored_lines': filter.ignored_lines,
                'column_name': filter.column_name,
                'column_date': filter.column_date,
                'column_date_val': filter.column_date_val,
                'amount_separated': filter.amount_separated,
                'column_debit': filter.column_debit,
                'column_credit': filter.column_credit,
                'column_ref': filter.column_ref,
                'column_note': filter.column_note,
                'encoding': filter.encoding or 'utf-8',
                'encoding_other': filter.encoding_other,
                'thousand_separator': filter.thousand_separator,
                'text_separator': filter.text_separator,
                }
        import_wiz = import_obj.create(vals)
        try:
            import_wiz.file_parsing()
            self.write({
                        'error_msg': import_wiz.note,
                        'state': 'imported',
                        })
        except Exeption as e:
            self.write({
                        'error_msg': e,
                        'state': 'error',
                        })

    @api.one
    def set_draft(self):
        self.state = 'draft'

    def cron_import_files(self, cr, uid, context=None):
        """
        CRON importing files into the bank statements
        """
        active_ids = self.search(cr, uid, [
                                           ('state', '=', 'draft'),
                                           ], context=context)
        self.import_files(cr, uid, active_ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: