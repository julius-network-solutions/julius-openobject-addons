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
from openerp import models, _

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

    #TODO: check this method
    def create(self, cr, uid, vals, context=None):
        partner_vals = {
            'name' : (vals.get('first_name',False) or '') + ' ' + (vals.get('name',False) or ''),
            'customer': False,
            'supplier' : False,
            'employee' : True
        }
        address_obj = self.pool.get('res.partner')
        partner_obj = self.pool.get('res.partner')
        if not vals.get('address_home_id',False):
            partner_id = partner_obj.create(cr, uid, partner_vals, context=context)
            data = {
                'active' : vals.get('active',True),
                'name' : (vals.get('first_name',False) or '') + ' ' + (vals.get('name',False) or ''),
                'function' : vals.get('function',False),
                'street' : vals.get('street',False),
                'street2' : vals.get('street2',False),
                'zip' : vals.get('zip',False),
                'city' : vals.get('city',False),
                'email' : vals.get('email',False),
                'phone' : vals.get('phone',False),
                'fax' : vals.get('fax',False),
                'mobile' : vals.get('mobile',False),
                'parent_id' : partner_id,
            }
            address_id = address_obj.create(cr, uid, data, context=context)
        
            vals.update({'address_home_id': address_id,})
        else:
            if not address_obj.browse(cr, uid, vals.get('address_home_id'), context=context).parent_id:
                partner_id = partner_obj.create(cr, uid, partner_vals, context=context)
                address_obj.write(cr, uid, vals.get('address_home_id'), {'parent_id': partner_id}, context=context)
        return super(hr_employee, self).create(cr, uid, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
