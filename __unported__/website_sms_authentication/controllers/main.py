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

from openerp import http, fields, _
from openerp.http import request


class website_sms_authentication(http.Controller):

    def preRenderThanks(self, code, values, kwargs):
        """ Allow to be overrided """
        return {
                '_values': values,
                '_kwargs': kwargs,
                }

    def callback_sms(self, code, values, kwargs):
        """ Allow to be overrided """
        return request.website.\
            render(kwargs.get("view_callback",
                              "website_sms_authentication.thanks"), values)

    @http.route([
                 '/sms-authentication/<int:code_id>',
                 '/sms-authentification/<int:code_id>',
                 ], type='http', auth="public", website=True)
    def sms_authentication(self, code_id, **kwargs):
        if not code_id:
            return request.website.render('website.404')
        env = request.env(context=dict(request.context))
        values = dict(kwargs)
        error = {}
        code_obj = env['sms.authentication']
        code = code_obj.sudo().search([('id', '=', code_id)], limit=1)
        if not code:
            return request.website.render('website.404')
        if code.validity <= fields.Datetime.now() or code.state == 'cancel':
            error['expired'] = True
            values.update({
                           'code': code,
                           'error': error,
                           })
            return request.website.\
                render('website_sms_authentication.sms_authentication', values)
        for field in ['code']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        written_code = 'code' in values and values['code'] and \
            values.pop('code') or False
        if not written_code:
            pass
        elif not code.verify_code(written_code):
            error['wrong_code'] = True
        else:
            values = self.preRenderThanks(code, values, kwargs)
            return self.callback_sms(code, values, kwargs)
        values.update({
                       'code': code,
                       'error': error,
                       })
        return request.website.\
            render('website_sms_authentication.sms_authentication', values)

    @http.route([
                 '/sms-authentication-new-code/<int:code_id>',
                 '/sms-authentification-nouveau-code/<int:code_id>',
                 ], type='http', auth="public", website=True)
    def sms_authentication_new_code(self, code_id, **kwargs):
        if not code_id:
            return request.website.render('website.404')
        env = request.env(context=dict(request.context))
        values = dict(kwargs)
        error = {}
        code_obj = env['sms.authentication']
        code = code_obj.sudo().search([('id', '=', code_id)], limit=1)
        if not code:
            return request.website.render('website.404')
        code = code.send_new_code()
        values.update({
                       'code': code,
                       'error': error,
                       })
        return request.website.\
            render('website_sms_authentication.sms_authentication', values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
