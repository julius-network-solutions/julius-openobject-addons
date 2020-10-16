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

class point_attendance(models.TransientModel):
    _name = 'point.partner.attendance'
    _description = 'Point Partner attendance'

    partner_id = fields.\
        Many2one('res.partner', 'Partner', required=True,
                 default=lambda self: self._context.get('partner_id'))
    state = fields.Selection([
                              ('absent', 'Absent'),
                              ('present', 'Present'),
                              ], string='Actual state',
                             compute='_get_state')

    @api.depends('partner_id')
    def _get_state(self):
        state = 'absent'
        if self.partner_id:
            self._cr.execute('SELECT hr_attendance.action, \
                             hr_attendance.partner_id \
                             FROM ( \
                                   SELECT MAX(name) AS name, partner_id \
                                   FROM hr_attendance \
                                   WHERE action in (\'sign_in\', \
                                                    \'sign_out\') \
                                   AND type = \'partner\' \
                                   GROUP BY partner_id \
                                   ) AS foo \
                             LEFT JOIN hr_attendance \
                                 ON (hr_attendance.partner_id = \
                                     foo.partner_id \
                                     AND hr_attendance.name = foo.name) \
                             WHERE hr_attendance.partner_id = %s',
                             (self.partner_id.id,))
        for res in self._cr.fetchall():
            state = res[0] == 'sign_in' and 'present' or 'absent'
        self.state = state

    @api.one
    def sign_in(self):
        attendance_obj = self.env['hr.attendance']
        attendance_obj.create({
                               'partner_id': self.partner_id.id,
                               'type': 'partner',
                               'employee_id': False,
                               'action': 'sign_in',
                               })

    @api.one
    def sign_out(self):
        attendance_obj = self.env['hr.attendance']
        attendance_obj.create({
                               'partner_id': self.partner_id.id,
                               'type': 'partner',
                               'employee_id': False,
                               'action': 'sign_out',
                               })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
