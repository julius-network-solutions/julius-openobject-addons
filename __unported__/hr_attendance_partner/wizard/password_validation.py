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
from openerp.exceptions import Warning

class attendance_password_validation(models.TransientModel):
    _name = 'attendance.password.validation'
    _description = 'Attendance Password validation'

    password = fields.Char()
    partner_id = fields.\
        Many2one('res.partner', 'Partner', required=True,
                 default=lambda self: self._context.get('partner_id'))

    @api.multi
    def validate(self):
        assert len(self) == 1, 'This option should only be ' \
            'used for a single id at a time.'
        if self.partner_id.attendance_password != self.password:
            raise Warning(_('Password error !'))
        action = self.env.\
            ref('hr_attendance_partner.action_point_partner_attendance_form')
        if action:
            result = action.read()[0]
            result['context'] = {'partner_id': self.partner_id.id}
            return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
