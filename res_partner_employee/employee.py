# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.osv import fields
from openerp import models, api, _

class hr_employee(models.Model):
    _inherit = "hr.employee"
    _columns = {
                'street': fields.related('address_home_id', 'street', string='Street', type='char', size=128),
                'street2': fields.related('address_home_id', 'street2', string='Street2', type='char', size=128),
                'zip': fields.related('address_home_id', 'zip', string='Zip', type='char', size=24),
                'city': fields.related('address_home_id', 'city', string='City', type='char', size=128),
                'email': fields.related('address_home_id', 'email', string='E-mail', type='char', size=128),
                'phone': fields.related('address_home_id', 'phone', string='Phone', type='char', size=64),
                'fax': fields.related('address_home_id', 'fax', string='Fax', type='char', size=64),
                'mobile': fields.related('address_home_id', 'mobile', string='Mobile', type='char', size=64),
                }

    @api.model
    def _get_default_partner_values(self, vals):
        """
        Get the default values to create automatically the address_home_id
        """
        partner_vals = {
                        'name': vals.get('name', False) or '',
                        'customer': False,
                        'supplier': False,
                        'employee': True,
                        'active' : vals.get('active', True),
                        'function' : vals.get('function', False),
                        'street' : vals.get('street', False),
                        'street2' : vals.get('street2', False),
                        'zip' : vals.get('zip', False),
                        'city' : vals.get('city', False),
                        'email' : vals.get('email', False),
                        'phone' : vals.get('phone', False),
                        'fax' : vals.get('fax', False),
                        'mobile' : vals.get('mobile', False),
                        }
        return partner_vals

    @api.model
    def create(self, vals):
        partner_obj = self.env['res.partner']
        if not vals.get('address_home_id', False):
            partner_vals = self._get_default_partner_values(vals)
            partner = partner_obj.create(partner_vals)
            vals.update({'address_home_id': partner.id,})
        return super(hr_employee, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
