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

from openerp import models, fields, api, _

class res_partner(models.Model):
    _inherit = 'res.partner'

    partner_user_id = fields.Many2one('res.users', 'Partner\'s Login')

    @api.model
    def _get_default_user_vals(self, partner):
        users_obj = self.env['res.users']
        default_name = partner.name
        name = default_name
        i = 1
        start = True
        while True:
            if start:
                start = False
            else:
                name = default_name + str(i)
            if not users_obj.search([('login', '=', name)]):
                break
            i += 1
        return {
                'partner_id': partner.id,
                'login': name,
                'password': name,
                }

    @api.multi
    def create_user(self):
        user_obj = self.env['res.users']
        for partner in self:
            if not partner.partner_user_id:
                if partner.user_ids:
                    partner.partner_user_id = partner.user_ids[0]
                else:
                    user_vals = partner._get_default_user_vals(self)
                    if user_vals:
                        user = user_obj.with_context(do_not_update=1).\
                            create(user_vals)
                        partner.partner_user_id = user
                

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: