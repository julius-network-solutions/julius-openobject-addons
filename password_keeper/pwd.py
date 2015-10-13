# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 credativ ltd. <info@credativ.co.uk>
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
#################################################################################
from openerp import models, fields, api, _

class res_password(models.Model):
    _name = "res.password"

    name            = fields.Char('Title')
    user            = fields.Char('User')
    url             = fields.Char('URL')
    password        = fields.Char('Password')
    group_id        = fields.Many2one('res.groups','Group')
    user_id         = fields.Many2one('res.users',
                                      'Owner',
                                      readonly=1,
                                      default=lambda self: self.env.user)

    @api.one
    def generate(self):
        import random
        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        pw_length = 8
        mypw = ""
        for i in range(pw_length):
            next_index = random.randrange(len(alphabet))
            mypw = mypw + alphabet[next_index]

        if not self.read(['password'])[0]['password']:
            self.write({'password':mypw})
        return

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
