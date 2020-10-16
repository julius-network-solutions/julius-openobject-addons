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

from openerp import models, fields, api


class signature_config_settings(models.TransientModel):
    _inherit = 'base.config.settings'
    
    signature_key = fields.Char("Signature key")
    signature_passphrase = fields.Char("Signature pass phrase")

    @api.one
    def set_signature_key(self):
        params = self.env['ir.config_parameter']
        params.set_param('attachment_signature_key',
                         self.signature_key or '',
                         groups=['base.group_system'])
        params.set_param('attachment_signature_passphrase',
                         self.signature_passphrase or '',
                         groups=['base.group_system'])

    @api.model
    def default_get(self, fields_list):
        result = super(signature_config_settings, self).\
        default_get(fields_list)
        params = self.env['ir.config_parameter']
        signature_key = params.\
            get_param('attachment_signature_key',
                      default='')
        signature_passphrase = params.\
            get_param('attachment_signature_passphrase',
                      default='')
        result.update({
                       'signature_key': signature_key,
                       'signature_passphrase': signature_passphrase,
                       })
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
