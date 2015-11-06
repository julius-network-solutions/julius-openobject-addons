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
from openerp import models, fields, api, _
from openerp.osv import orm
import hmac, base64, struct, hashlib, time

class res_users(models.Model):
    _inherit = 'res.users'
    
    password_api_key = fields.Char('Password', size=16)

    @api.one
    def generate(self):
        import random
        alphabet = "234567ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        pw_length = 16
        mypw = ""
        for i in range(pw_length):
            next_index = random.randrange(len(alphabet))
            mypw = mypw + alphabet[next_index]

        if not self.read(['password_api_key'])[0]['password_api_key']:
            self.write({'password_api_key':mypw})
        return

class google_auth_wiz(models.TransientModel):
    _name = 'google.auth.wiz'
    
    validation_code = fields.Char('Validation Code', size=6)
    
    @api.multi
    def get_hotp_token(self, secret, intervals_no):
        key = base64.b32decode(secret, True)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = ord(h[19]) & 15
        h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
        return h
    
    @api.multi
    def get_totp_token(self, secret):
        user = self.env['res.users'].browse(self._uid)
        self = self.with_context(tz=user.tz)
        secret = user.password_api_key
        h = self.get_hotp_token(secret, intervals_no=int(time.time())//30)
        print time.time()
        print h
        print self.validation_code
        domain = []
        h = str(h)
        if self.validation_code == h:
            return {
              'name': _('Password Manager'),
              'view_type': 'form',
              'view_mode': 'tree,form',
              'res_model': 'res.password',
              'domain': domain,
              'type': 'ir.actions.act_window',
            }
        else: 
            raise orm.except_orm('Wrong Code', 'Please Retry, %s,  %s, %s ' % (time.time(), h, self.validation_code))
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
