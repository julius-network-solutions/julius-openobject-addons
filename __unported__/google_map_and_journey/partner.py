# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, api

class res_partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_url_parameters_partner_vals(self, partner):
        info = []
        if partner.street:
            info.append(partner.street)
        if partner.city:
            info.append(partner.city)
        if partner.state_id:
            info.append(partner.state_id.name)
        if partner.country_id:
            info.append(partner.country_id.name)
        if partner.zip:
            info.append(self.zip)
        return '+'.join(info).replace(' ', '+')

    @api.multi
    def open_map(self):
        base_url = "http://maps.google.com/maps?oi=map&q="
        for partner in self:
            url = base_url + self._get_url_parameters_partner_vals(partner)
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                    }

    @api.multi
    def open_journey(self):
        user_obj = self.env['res.users']
        company = user_obj.sudo().browse(self._uid).company_id
        base_url = "http://maps.google.com/maps?saddr="
        company_url_parameters = self.\
            _get_url_parameters_partner_vals(company.partner_id)
        for partner in self:
            partner_url_parameters = self.\
                _get_url_parameters_partner_vals(partner)
            
        url = "%s%s&daddr=%s" % (base_url,
                                 company_url_parameters,
                                 partner_url_parameters)
        return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

