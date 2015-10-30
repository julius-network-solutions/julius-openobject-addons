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

from random import uniform
from datetime import datetime, timedelta
from openerp import models, fields, api


class sms_authentication(models.Model):
    _name = 'sms.authentication'
    _description = 'SMS authentication'

    @api.model
    def _generate_code(self, number=6):
        """
        This method will generate a code.
        """
        val = 1
        for i in range(number):
            val *= 10
        value_code = int(uniform(1,9) * 100000)
        return value_code

    _order = 'validity DESC'

    name = fields.Char('Code', required=True, readonly=True,
                       states={'draft': [('readonly', False)]},
                       default=_generate_code)
    mobile = fields.Char('Mobile number', required=True, readonly=True,
                         states={'draft': [('readonly', False)]})
    validity = fields.Datetime('Validity', readonly=True,
                               states={'draft': [('readonly', False)]})
    gateway_id = fields.Many2one('sms.smsclient',
                                 'SMS Gateway', readonly=True,
                                 states={'draft': [('readonly', False)]})
    state = fields.Selection([
                              ('draft', 'Draft'),
                              ('sent', 'Sent'),
                              ('not_valid', 'Not valid'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel'),
                              ], 'State', readonly=True, default='draft')

    @api.one
    def verify_code(self, code=None):
        """
        Method checking the code send to the mobile number
        """
        if self.validity < fields.Datetime.now():
            self.state = 'cancel'
            return
        if self.state in ('sent', 'not_valid'):
            state = 'not_valid'
            if self.name == code:
                state = 'done'
            self.write({
                        'state': state,
                        })

    @api.one
    def send_code(self):
        """
        Method sending the code to the mobile number
        """
        if self.state == 'draft':
            mobile = self.mobile
            mobile = '0634456091'
            self.write({
                        'state': 'sent',
                        'validity': datetime.now() + timedelta(minutes=15),
                        })

    @api.one
    def send_new_code(self):
        """
        Method sending a new code to the mobile number
        """
        default = {
                   'name': self._generate_code(),
                   'validity': False,
                   'state': 'draft',
                   }
        new = self.copy(default=default)
        self.state = 'cancel'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
