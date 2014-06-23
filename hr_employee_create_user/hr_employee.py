# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    
    def _get_default_user_vals(self, cr, uid, employee, context=None):
        default_name = employee.name
        name = default_name
        i = 1
        start = True
        while True:
            if start:
                start = False
            else:
                name = default_name + str(i)
            if not self.search(cr, uid, [('login', '=', name)], context=context):
                break
            i += 1
        vals = {
            'name': employee.name.upper() + (employee.first_name and ' ' + employee.first_name.title() or ''),
            'login': name,
            'password': name,
        }
        return vals
    
    def create_user(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        for employee in self.browse(cr, uid, ids, context=context):
            employee_name = employee.name.upper() + (employee.first_name and ' ' + employee.first_name.title() or '')
            if not employee.user_id or employee.user_id.name != employee_name:
                user_vals = self._get_default_user_vals(cr, uid, employee, context=context)
                user_id = self.pool.get('res.users').create(cr, uid, user_vals, context=context)
                self.write(cr, uid, employee.id, {'user_id': user_id}, context=context)
        return True
    
hr_employee()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: