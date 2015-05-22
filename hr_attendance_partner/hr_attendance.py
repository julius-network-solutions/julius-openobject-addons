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

    def _altern_si_so(self, cr, uid, ids, context=None):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.
        """
        for att in self.browse(cr, uid, ids, context=context):
            # search and browse for first previous and first next records
            if att.type == 'partner':
                prev_att_ids = self.\
                    search(cr, uid, [
                                     ('partner_id', '=', att.partner_id.id),
                                     ('name', '<', att.name),
                                     ('action', 'in', ('sign_in', 'sign_out')),
                                     ], limit=1, order='name DESC')
                next_add_ids = self.\
                    search(cr, uid, [
                                     ('partner_id', '=', att.partner_id.id),
                                     ('name', '>', att.name),
                                     ('action', 'in', ('sign_in', 'sign_out')),
                                     ], limit=1, order='name ASC')
                prev_atts = self.browse(cr, uid, prev_att_ids, context=context)
                next_atts = self.browse(cr, uid, next_add_ids, context=context)
                # check for alternance, return False if at least one condition is not satisfied
                if prev_atts and prev_atts[0].action == att.action: # previous exists and is same action
                    return False
                if next_atts and next_atts[0].action == att.action: # next exists and is same action
                    return False
                if (not prev_atts) and (not next_atts) and att.action != 'sign_in': # first attendance must be sign_in
                    return False
            else:
                prev_att_ids = self.\
                    search(cr, uid, [
                                     ('employee_id', '=', att.employee_id.id),
                                     ('name', '<', att.name),
                                     ('action', 'in', ('sign_in', 'sign_out')),
                                     ], limit=1, order='name DESC')
                next_add_ids = self.\
                    search(cr, uid, [
                                     ('employee_id', '=', att.employee_id.id),
                                     ('name', '>', att.name),
                                     ('action', 'in', ('sign_in', 'sign_out')),
                                     ], limit=1, order='name ASC')
                prev_atts = self.browse(cr, uid, prev_att_ids, context=context)
                next_atts = self.browse(cr, uid, next_add_ids, context=context)
                # check for alternance, return False if at least one condition is not satisfied
                if prev_atts and prev_atts[0].action == att.action: # previous exists and is same action
                    return False
                if next_atts and next_atts[0].action == att.action: # next exists and is same action
                    return False
                if (not prev_atts) and (not next_atts) and att.action != 'sign_in': # first attendance must be sign_in
                    return False
        return True

    _constraints = [(_altern_si_so,
                     'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)',
                     ['action'])]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
