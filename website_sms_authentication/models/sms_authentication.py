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

from random import uniform
from datetime import datetime, timedelta
from openerp import models, fields, api
import re


class sms_authentication(models.Model):
    _name = 'sms.authentication'
    _description = 'SMS authentication'

    @api.model
    def _select_objects(self):
        model_pool = self.env['ir.model']
        models = model_pool.search([], limit=None)
        return [(r.model, r.name) for r in models] + [('', '')]

    @api.model
    def _generate_code(self, number=6):
        """
        This method will generate a code.
        """
        val = 1
        for i in range(number):
            val *= 10
        value_code = int(uniform(1,9) * 100000)
        return value_code

    _order = 'validity DESC'

    name = fields.Char('Code', required=True, readonly=True,
                       states={'draft': [('readonly', False)]},
                       default=_generate_code)
    type = fields.Selection([
                             ('sms', 'SMS'),
                             ('email', 'Email'),
                             ], 'Type', required=True, readonly=True,
                            states={'draft': [('readonly', False)]},
                            default='sms',)
    mobile = fields.Char('Mobile number', readonly=True,
                         states={'draft': [('readonly', False)]})
    queue_id = fields.Many2one('sms.smsclient.queue', 'SMS Queue',
                               readonly=True)
    template_id = fields.Many2one('email.template', 'SMS or Email template')
    email = fields.Char('Email address', readonly=True,
                        states={'draft': [('readonly', False)]})
    validity = fields.Datetime('Validity', readonly=True,
                               states={'draft': [('readonly', False)]})
    res_model = fields.Char('Res model')
    res_id = fields.Integer('Res id')
    link_id = fields.Reference(string='Link', selection=_select_objects,
                               compute='_get_reference_link')

    @api.one
    def _get_reference_link(self):
        link_id = False
        if self.res_model and self.res_id:
            link_id = "%s,%s" % (self.res_model, self.res_id)
        self.link_id = link_id

    state = fields.Selection([
                              ('draft', 'Draft'),
                              ('queued', 'Queued'),
                              ('sent', 'Sent'),
                              ('not_valid', 'Not valid'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel'),
                              ('error', 'Error'),
                              ], 'State', readonly=True, default='draft')

    @api.one
    def set_to_draft(self, test=False):
        """
        Set the SMS to draft if in error
        """
        if self.state == 'error':
            self.state = 'draft'

    @api.multi
    def verify_code(self, code=None):
        """
        Method checking the code send to the mobile number
        """
        assert len(self.ids) == 1, \
            "This function should only be used for a single id at a time"
        if self.state != 'done' and \
            self.validity <= fields.Datetime.now():
            self.state = 'cancel'
            return False
        if self.state in ('sent', 'not_valid'):
            state = 'not_valid'
            result = False
            if self.name == code:
                state = 'done'
                result = True
            self.write({
                        'state': state,
                        })
            return result
        return False

    @api.model
    def _prepare_smsclient_queue(self, record, sms_data):
        geteway = record.template_id.gateway_id
        return {
                'name': sms_data.get('subject'),
                'gateway_id': geteway.id,
                'state': 'draft',
                'mobile': record.mobile,
                'msg': sms_data.get('sms_text'),
                'validity': geteway.validity,
                'classes': geteway.classes,
                'deferred': geteway.deferred,
                'priority': geteway.priority,
                'coding': geteway.coding,
                'nostop': geteway.nostop,
                }

    @api.one
    def send_code(self):
        """
        Method sending the code to the mobile number
        """
        state = self.state
        template = self.template_id
        if not self.validity:
            self.validity = datetime.now() + timedelta(minutes=15)
        if self.state == 'draft':
            if self.type == 'sms':
                queue_obj = self.env['sms.smsclient.queue']
                mobile = self.mobile
                sms = template.generate_email(template.id, self.id)
                body = sms.get('body')
                if not body:
                    body = sms.get('body_html')
                if body:
                    if '<br>' in body:
                        body = body.replace('<br>', '\n')
                    p = re.compile(r'<.*?>')
                    text = p.sub('', body)
                    sms['sms_text'] = text
                queue_vals = self._prepare_smsclient_queue(self, sms)
                queue = queue_obj.create(queue_vals)
                queue.send_sms()
                self.queue_id = queue.id
                if queue.state == 'send':
                    state = 'sent'
                elif queue.state == 'error':
                    state = 'error'
                else:
                    state = 'queued'
            elif self.type == 'email':
                email = self.email
                template.send_mail(self.id, force_send=True)
                state = 'sent'
        if self.state != state:
            self.state = state

    @api.multi
    def send_new_code(self):
        """
        Method sending a new code to the mobile number
        """
        assert len(self.ids) == 1, \
            "This function should only be used for a single id at a time"
        default = {
                   'name': self._generate_code(),
                   'validity': False,
                   'queue_id': False,
                   'state': 'draft',
                   }
        new = self.copy(default=default)
        new.send_code()
        self.state = 'cancel'
        if self.type == 'sms' and self.queue_id:
            self.queue_id.cancel_sms()
        return new

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
