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

import logging
_logger = logging.getLogger(__name__)
crypto_install = False
try:
    from M2Crypto import RSA
    crypto_install = True
    from M2Crypto.RSA import RSAError
except:
    _logger.warning("ERROR IMPORTING M2Crypto, if not installed, "
                    "please install it.\nGet it here: "
                    "https://pypi.python.org/pypi/M2Crypto")
import base64, hashlib
from openerp import models, fields, api, _
from openerp.exceptions import MissingError, Warning


class ir_attachment_signature_test(models.Model):
    _name = 'ir.attachment.signature.test'
    _description = 'Test document signature'

    datas = fields.Binary('Document to test', required=True)
    attachment_tested_id = fields.\
        Many2one('ir.attachment', 'Attachment',
                 default=lambda self: self._context.get('active_id'))
    force_signature = fields.Boolean('Force signature', default=False)
    signature_tested = fields.Text('Signature to test')

    @api.one
    def verify_attachment(self):
        if not crypto_install:
            raise MissingError("ERROR IMPORTING M2Crypto, if not installed, "
                               "please install it.\nGet it here:\n"
                               "https://pypi.python.org/pypi/M2Crypto")
        signature = self.signature_tested
        if self.force_signature:
            if not self.signature_tested:
                raise MissingError("Please set a key to test")
        else:
            signature = self.attachment_tested_id.signed_content
            if not signature:
                raise MissingError("This document have't been signed.")
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
        att = self.env['ir.attachment'].create({
                                                'name': 'File tested',
                                                'datas': self.datas,
                                                'datas_fname': 'File tested',
                                                'res_model': self._name,
                                                'res_id': self.id,
                                                })
        value = att.datas
        signature = base64.decodestring(signature)
        sha256_val = hashlib.sha256(value).digest()
        try:
            pkey.verify(sha256_val, signature)
            raise Warning(_("The signature is OK !\n"
                            "This document hasn't been changed."))
        except RSAError:
            raise Warning(_("Wrong signature !\nThe document has changed."))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
