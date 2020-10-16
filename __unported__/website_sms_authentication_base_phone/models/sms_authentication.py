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

from openerp import models, fields


class sms_authentication(models.Model):
    _name = 'sms.authentication'
    _description = 'SMS authentication'
    _inherit = ['sms.authentication', 'phone.common']
    _phone_fields = ['mobile']
    _phone_name_sequence = 10
    _country_field = 'country_id'
    _partner_field = None

    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, None, vals, context=context)
        return super(sms_authentication, self).create(
            cr, uid, vals_reformated, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, ids, vals, context=context)
        return super(sms_authentication, self).write(
            cr, uid, ids, vals_reformated, context=context)

    mobile = fields.Char('Mobile number', readonly=True,
                         states={'draft': [('readonly', False)]})
    country_id = fields.Many2one('res.country', 'Country')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
