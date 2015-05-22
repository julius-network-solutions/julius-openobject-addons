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

from openerp import models, fields, api, _

class hr_attendance(models.Model):
    _inherit = "hr.attendance"

    type = fields.Selection([
                             ('employee', 'Employee'),
                             ('partner', 'Partner'),
                             ], default='employee', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    employee_id = fields.Many2one(required=False)

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'partner':
            self.employee_id = False
        else:
            self.partner_id = False
            employees = self.env['hr.employee'].\
                search([
                        ('user_id', '=', self._uid)
                        ], limit=1)
            self.employee_id = employees.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
