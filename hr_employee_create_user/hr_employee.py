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

from openerp import models, api, _

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def _get_default_user_vals(self):
        default_name = self.name
        name = default_name
        i = 1
        start = True
        while True:
            if start:
                start = False
            else:
                name = default_name + str(i)
            if not self.search([('login', '=', name)]):
                break
            i += 1
        return {
            'name': self.name,
            'login': name,
            'password': name,
        }

    @api.multi
    def create_user(self):
        user_obj = self.env['res.users']
        for employee in self:
            if not employee.user_id:
                user_vals = employee._get_default_user_vals()
                if isinstance(user_vals, list):
                    user_vals = user_vals and user_vals[0] or {}
                if user_vals:
                    user = user_obj.create(user_vals)
                    employee.user_id = user
                

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: