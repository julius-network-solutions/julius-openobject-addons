# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models


class res_partner(models.Model):
    _inherit = 'res.partner'

    def signup_retrieve_info(self, cr, uid, token, context=None):
        res = super(res_partner, self).signup_retrieve_info(cr, uid, token, context=context)
        if res.get('name'):
            partner = self._signup_retrieve_partner(cr, uid, token, check_validity=False, raise_exception=False, context=context)
            if partner.firstname:
                res['firstname'] = partner.firstname
                res['lastname'] = partner.lastname
                del res['name']
        return res

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
