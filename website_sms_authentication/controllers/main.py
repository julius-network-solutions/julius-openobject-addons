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

from openerp import http, _
from openerp.http import request


class website_sms_authentication(http.Controller):

    @http.route([
                 '/sms-authentication/<int:code_id>',
                 '/sms-authentification/<int:code_id>',
                 ], type='http', auth="public", website=True)
    def sms_authentication(self, code_id, **kwargs):
        if not code_id:
            return request.website.render('website.404')
        env = request.env(context=dict(request.context))
        code_obj = env['sms.authentication']
        code = code_obj.sudo().search([('id', '=', code_id)], limit=1)
        if not code:
            return request.website.render('website.404')
        values = {}
        values.update(kwargs=kwargs.items())
        error = {}
        values.update({
                       'code': code,
                       'error': error,
                       })
        return request.website.\
            render('website_sms_authentication.sms_authentication', values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
