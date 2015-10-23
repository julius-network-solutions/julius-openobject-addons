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

from M2Crypto import RSA
import base64, hashlib
from openerp import models, fields, api
from openerp.exceptions import MissingError


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    signed_content = fields.Text('Signed Content', readonly=True)

    @api.one
    def sign_attachment(self):
        params = self.env['ir.config_parameter']
        def _get_key():
            signature_key = params.sudo().\
                get_param('attachment_signature_key',
                          default='')
            return signature_key
        def gimmepw(*args):
            signature_passphrase = params.sudo().\
                get_param('attachment_signature_passphrase',
                          default='')
            return str(signature_passphrase)
        key = _get_key()
        pkey = RSA.load_key(key, gimmepw)
        value = self.datas
        sha256_val = hashlib.sha256(value).digest()
        signature = pkey.sign(sha256_val)
        self.signed_content = base64.encodestring(signature)

    @api.one
    def verify_attachment(self):
        params = self.env['ir.config_parameter']
        def _get_key():
            signature_key = params.sudo().\
                get_param('attachment_signature_key',
                          default='')
            return signature_key
        def gimmepw(*args):
            signature_passphrase = params.sudo().\
                get_param('attachment_signature_passphrase',
                          default='')
            return signature_passphrase
        key = _get_key()
        pkey = RSA.load_key(key, gimmepw)
        value = open('/home/jules/Bureau/file', 'rb').read()
        sha256_val = hashlib.sha256(value).digest()
        signature = self.signed_content
        pkey.verify(sha256_val, signature)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
