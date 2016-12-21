# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import time
import urllib
import requests, json
from openerp import models, fields, api, _
from openerp.exceptions import except_orm

import logging
_logger = logging.getLogger(__name__)


class partner_sms_send(models.Model):
    _name = "partner.sms.send"
    _description = "Partner SMS Send"

    def _default_get_mobile(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        partner_pool = self.pool.get('res.partner')
        active_ids = fields.get('active_ids')
        res = {}
        i = 0
        for partner in partner_pool.browse(cr, uid, active_ids, context=context):
            i += 1
            res = partner.mobile
        if i > 1:
            raise except_orm(_('Error'), _('You can only select one partner'))
        return res

    def _default_get_gateway(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway_ids = sms_obj.search(cr, uid, [], limit=1, context=context)
        return gateway_ids and gateway_ids[0] or False

    def onchange_gateway(self, cr, uid, ids, gateway_id, context=None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        if not gateway_id:
            return {}
        gateway = sms_obj.browse(cr, uid, gateway_id, context=context)
        return {
            'value': {
                'validity': gateway.validity,
                'classes': gateway.classes,
                'deferred': gateway.deferred,
                'priority': gateway.priority,
                'coding': gateway.coding,
                'tag': gateway.tag,
                'nostop': gateway.nostop,
            }
        }

    mobile_to = fields.Char('To', size=256, required=True)
    app_id = fields.Char('API ID', size=256)
    user = fields.Char('Login', size=256)
    password = fields.Char('Password', size=256)
    text = fields.Text('SMS Message', required=True)
    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', required=True)
    validity = fields.Integer('Validity',
                              help="the maximum time -in minute(s)- "
                              "before the message is dropped")
    classes = fields.Selection([
                                ('0', 'Flash'),
                                ('1', 'Phone display'),
                                ('2', 'SIM'),
                                ('3', 'Toolkit')
                                ], 'Class',
                               help="The sms class: flash(0), "
                               "phone display(1), SIM(2), toolkit(3)")
    deferred = fields.Integer('Deferred',
                              help="The time -in minute(s)- "
                              "to wait before sending the message")
    priority = fields.Selection([
                                 ('0', '0'),
                                 ('1', '1'),
                                 ('2', '2'),
                                 ('3', '3')
                                 ], 'Priority',
                                help="The priority of the message")
    coding = fields.Selection([
                               ('1', '7 bit'),
                               ('2', 'Unicode')
                               ], 'Coding',
                              help="The SMS coding: 1 for 7 bit "
                              "or 2 for unicode")
    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Boolean('NoStop',
                            help="Do not display STOP clause in the message, "
                            "this requires that this is not an "
                            "advertising message")

    _defaults = {
                 'mobile_to': _default_get_mobile,
                 'gateway': _default_get_gateway,
                 }

    def sms_send(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        client_obj = self.pool.get('sms.smsclient')
        for data in self.browse(cr, uid, ids, context=context):
            if not data.gateway:
                raise except_orm(_('Error'), _('No Gateway Found'))
            else:
                client_obj._send_message(cr, uid, data, context=context)
        return {}


class SMSClient(models.Model):
    _name = 'sms.smsclient'
    _description = 'SMS Client'

    name = fields.Char('Gateway Name', size=256, required=True)
    url = fields.Char('Gateway URL', size=256,
                      required=True, help='Base url for message')
    property_ids = fields.One2many('sms.smsclient.parms',
                                   'gateway_id', 'Parameters')
    history_line = fields.One2many('sms.smsclient.history',
                                   'gateway_id', 'History')
    method = fields.Selection([
                               ('http', 'HTTP Method'),
                               ('smpp', 'SMPP Method'),
                               ('primo', 'Primo Method'),
                               ('ovh', 'Api OVH'),
                               ], 'API Method', select=True, default='http')
    state = fields.Selection([
                              ('new', 'Not Verified'),
                              ('waiting', 'Waiting for Verification'),
                              ('confirm', 'Verified'),
                              ], 'Gateway Status', select=True,
                             readonly=True, default='new')
    users_id = fields.Many2many('res.users', 'res_smsserver_group_rel',
                                'sid', 'uid', 'Users Allowed')
    code = fields.Char('Verification Code', size=256)
    body = fields.Text('Message',
                       help="The message text that will be send along "
                       "with the email which is send through this server")
    validity = fields.Integer('Validity', default=10,
                              help="The maximum time -in minute(s)- "
                              "before the message is dropped")
    classes = fields.Selection([
                                ('0', 'Flash'),
                                ('1', 'Phone display'),
                                ('2', 'SIM'),
                                ('3', 'Toolkit')
                                ], 'Class', default='1',
                               help="The SMS class: flash(0),phone "
                               "display(1),SIM(2),toolkit(3)")
    deferred = fields.Integer('Deferred', default=0,
                              help="The time -in minute(s)- to wait "
                              "before sending the message")
    priority = fields.Selection([
                                 ('0', '0'),
                                 ('1', '1'),
                                 ('2', '2'),
                                 ('3', '3')
                                 ], 'Priority', default='3',
                                help="The priority of the message")
    coding = fields.Selection([
                               ('1', '7 bit'),
                               ('2', 'Unicode')
                               ], 'Coding', default='1',
                              help="The SMS coding: 1 for 7 bit "
                              "or 2 for unicode")
    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Boolean('NoStop', default=True,
                            help="Do not display STOP clause in the message, "
                            "this requires that this is not an "
                            "advertising message")
    char_limit = fields.Boolean('Character Limit', default=True)
    raise_exception = fields.Boolean('Raise exception', default=False)

    def _check_permissions(self, cr, uid, id, context=None):
        cr.execute("SELECT * FROM res_smsserver_group_rel "
                   "WHERE sid=%s AND uid=%s" % (id, uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    def _prepare_smsclient_queue(self, cr, uid, data, name, context=None):
        return {
                'name': name,
                'gateway_id': data.gateway.id,
                'state': 'draft',
                'mobile': data.mobile_to,
                'msg': data.text,
                'validity': data.validity,
                'classes': data.classes,
                'deferred': data.deferred,
                'priority': data.priority,
                'coding': data.coding,
                'tag': data.tag,
                'nostop': data.nostop,
                }

    def _send_message(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        gateway = data.gateway
        if gateway:
            if not self._check_permissions(cr, uid, gateway.id, context=context):
                raise except_orm(_('Permission Error!'), _('You have no permission to access %s ') % (gateway.name,))
            url = gateway.url
            name = url
            if gateway.method == 'http':
                prms = {}
                for p in data.gateway.property_ids:
                     if p.type == 'user':
                         prms[p.name] = p.value
                     elif p.type == 'password':
                         prms[p.name] = p.value
                     elif p.type == 'to':
                         prms[p.name] = data.mobile_to
                     elif p.type == 'sms':
                         prms[p.name] = data.text
                     elif p.type == 'extra':
                         prms[p.name] = p.value
                     elif p.type == 'sender':
                         prms[p.name] = p.value
                params = urllib.urlencode(prms)
                name = url + "?" + params
            queue_obj = self.pool.get('sms.smsclient.queue')
            vals = self._prepare_smsclient_queue(cr, uid, data, name, context=context)
            queue_obj.create(cr, uid, vals, context=context)
        return True

    def _check_queue(self, cr, uid, context=None):
        if context is None:
            context = {}
        queue_obj = self.pool.get('sms.smsclient.queue')
        sids = queue_obj.search(cr, uid, [
                                          ('state', '=', 'draft'),
                                          ], limit=30, context=context)
        queue_obj.write(cr, uid, sids, {'state': 'sending'}, context=context)
        queue_obj.send_sms(cr, uid, sids, context=context)
        return True


class SMSQueue(models.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'

    name = fields.Text('SMS Request', size=256,
                       required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    msg = fields.Text('SMS Text', size=256,
                      required=True, readonly=True,
                      states={'draft': [('readonly', False)]})
    mobile = fields.Char('Mobile No', size=256,
                         required=True, readonly=True,
                         states={'draft': [('readonly', False)]})
    gateway_id = fields.Many2one('sms.smsclient',
                                 'SMS Gateway', readonly=True,
                                 states={'draft': [('readonly', False)]})
    state = fields.Selection([
                              ('draft', 'Queued'),
                              ('sending', 'Waiting'),
                              ('send', 'Sent'),
                              ('error', 'Error'),
                              ('cancel', 'Cancel'),
                              ], 'Message Status', select=True, readonly=True,
                             default='draft')
    error = fields.Text('Last Error', size=256,
                        readonly=True,
                        states={'draft': [('readonly', False)]})
    date_create = fields.Datetime('Date', readonly=True,
                                  default=fields.Datetime.now())
    validity = fields.Integer('Validity',
                              help="The maximum time -in minute(s)- "
                              "before the message is dropped")
    classes = fields.Selection([
                                ('0', 'Flash'),
                                ('1', 'Phone display'),
                                ('2', 'SIM'),
                                ('3', 'Toolkit')
                                ], 'Class',
                               help="The sms class: flash(0), "
                               "phone display(1), SIM(2), toolkit(3)")
    deferred = fields.Integer('Deferred',
                              help="The time -in minute(s)- to wait "
                              "before sending the message")
    priority = fields.Selection([
                                 ('0', '0'),
                                 ('1', '1'),
                                 ('2', '2'),
                                 ('3', '3'),
                                 ], 'Priority',
                                help='The priority of the message ')
    coding = fields.Selection([
                               ('1', '7 bit'),
                               ('2', 'Unicode')
                               ], 'Coding',
                              help="The sms coding: 1 for 7 bit "
                              "or 2 for unicode")
    tag = fields.Char('Tag', size=256,
                      help='An optional tag')
    nostop = fields.Boolean('NoStop',
                            help="Do not display STOP clause in the message, "
                            "this requires that this is not an "
                            "advertising message")

    @api.one
    def reset_to_draft(self, test=False):
        """
        Set the SMS to draft if in error
        """
        if self.state == 'error':
            self.state = 'draft'

    @api.one
    def cancel_sms(self, test=False):
        """
        Set the SMS to draft if in error
        """
        if self.state != 'send':
            self.state = 'cancel'

    @api.one
    def send_sms_by_primo(self, raise_exception=False):
        """
        Send SMS by the Primo method
        """
        for p in self.gateway_id.property_ids:
            if p.name == 'apikey':
                apikey = p.value
            elif p.type == 'sender':
                sender = p.value
        try:
            api_url = self.gateway_id.url
            message = ''
            if self.coding == '2':
                message = str(self.msg).decode('iso-8859-1').encode('utf8')
            if self.coding == '1':
                message = str(self.msg)
            data = {
                    'number': self.mobile,
                    'message': message,
                    'sender': sender,        
            }
            r = requests.post(api_url,
                              headers={'X-Primotexto-ApiKey':apikey,'Content-Type':'application/json'},
                              data=json.dumps(data))
            r.json()
            ### End of the new process ###
            self.state = 'send'
        except Exception, e:
            if raise_exception:
                raise except_orm('Error', e)
            else:
                self.write({
                            'state': 'error',
                            'error': str(e),
                            })

    @api.one
    def send_sms_by_http(self, raise_exception=False):
        """
        Send SMS by the HTTP method
        """
        raise_exception = self.gateway_id.raise_exception
        try:
            urllib.urlopen(self.name)
            self.state = 'send'
        except Exception, e:
            if raise_exception:
                raise except_orm('Error', e)
            else:
                self.write({
                            'state': 'error',
                            'error': str(e),
                            })

    @api.one
    def send_sms_by_smpp(self, raise_exception=False):
        """
        Send SMS by the SMPP method
        """
        for p in self.gateway_id.property_ids:
            if p.type == 'user':
                login = p.value
            elif p.type == 'password':
                pwd = p.value
            elif p.type == 'sender':
                sender = p.value
            elif p.type == 'sms':
                account = p.value
        try:
            from SOAPpy import WSDL
        except:
            error_msg = "ERROR IMPORTING SOAPpy, if not installed, " \
                "please install it: e.g.: apt-get install python-soappy"
            _logger.error(error_msg)
            if raise_exception:
                raise except_orm('Error', error_msg)
            else:
                self.write({
                            'state': 'error',
                            'error': str(error_msg),
                            })
            return
        try:
            _logger.info('enter sending process')
            soap = WSDL.Proxy(self.gateway_id.url)
            _logger.info('soap ok')
            message = ''
            if self.coding == '2':
                message = str(self.msg).decode('iso-8859-1').encode('utf8')
            elif self.coding == '1':
                message = str(self.msg)
            _logger.info(message)
            result = soap.\
                telephonySmsUserSend(str(login), str(pwd),
                                     str(account), str(sender),
                                     str(self.mobile), message,
                                     int(self.validity),
                                     int(self.classes),
                                     int(self.deferred),
                                     int(self.priority),
                                     int(self.coding),
                                     str(self.gateway_id.tag),
                                     int(self.gateway_id.nostop))
            _logger.info('sent')
            self.state = 'send'
            ### End of the new process ###
        except Exception, e:
            if raise_exception:
                raise except_orm('Error', e)
            else:
                self.write({
                            'state': 'error',
                            'error': str(e),
                            })
    @api.one
    def send_sms_by_ovh(self, raise_exception=False):
        """
        Send SMS by the SMPP method
        """
        endpoint = 'ovh-eu'
        application_key = ''
        application_secret = ''
        consumer_key = ''
        service_name = ''
        user = ''
        for p in self.gateway_id.property_ids:
            if p.type == 'sender':
                sender = p.value
            elif p.type == 'service_name':
                service_name = p.value
            elif p.type == 'user':
                user = p.value
            elif p.type == 'other':
                if p.name == 'application_key':
                    application_key = p.value
                elif p.name == 'application_secret':
                    application_secret = p.value
                elif p.name == 'consumer_key':
                    consumer_key = p.value
                account = p.value
        try:
            import ovh
        except:
            error_msg = "ERROR IMPORTING ovh, if not installed, " \
                "please install it: e.g.: " \
                "pip install -e git+https://github.com/ovh/python-ovh.git#egg=ovh"
            _logger.error(error_msg)
            if raise_exception:
                raise except_orm('Error', error_msg)
            else:
                self.write({
                            'state': 'error',
                            'error': str(error_msg),
                            })
            return
        try:
            _logger.info('enter sending process')
            client = ovh.Client(
                                endpoint=endpoint, # Endpoint of API OVH Europe (List of available endpoints)
                                application_key=application_key,    # Application Key
                                application_secret=application_secret, # Application Secret
                                consumer_key=consumer_key,       # Consumer Key
                                )
            _logger.info('Client ok')
            message = ''
            if self.coding == '2':
                message = str(self.msg).decode('iso-8859-1').encode('utf8')
            elif self.coding == '1':
                message = str(self.msg)
            _logger.info(message)
            url = '/sms/%s/users/%s/jobs' % (service_name, user)
            priority = 'high'
            if self.priority == '0':
                priority = 'veryLow'
            elif self.priority == '1':
                priority = 'low'
            elif self.priority == '2':
                priority = 'medium'
            coding = '7bit'
            if self.coding == '2':
                coding = '8bit'
            result = client.post(url,
                                 charset='UTF-8',
                                 coding=coding,
                                 message=message,
                                 noStopClause=self.gateway_id.nostop,
                                 priority=priority,
                                 receivers=[self.mobile],
                                 sender=sender,
                                 senderForResponse=False,
                                 validityPeriod=2880,
                                 )
            _logger.info('sent')
            self.state = 'send'
            ### End of the new process ###
        except Exception, e:
            if raise_exception:
                raise except_orm('Error', e)
            else:
                self.write({
                            'state': 'error',
                            'error': str(e),
                            })

    @api.model
    def _test_error_before_sending(self, record):
        """
        Method Checking if SMS valid before sending it
        @return: If the SMS can be send, return True,
            else return False
        """
        gateway = record.gateway_id
        if gateway.char_limit:
            if len(self.msg) > 160:
                error_text = _('Size of SMS should not be ' \
                               'more then 160 char')
                if gateway.raise_execption:
                    raise except_orm('Error',
                                     error_text)
                else:
                    record.write({
                                  'state': 'error',
                                  'error': error_text,
                                  })
                    return False
        return True

    @api.one
    def send_sms_by_method(self, method=None):
        """
        Method sending SMS from the queue by method
        """
        gateway = self.gateway_id
        if method == 'primo':
            self.send_sms_by_primo(raise_exception=gateway.raise_exception)
        elif method == 'http':
            self.send_sms_by_http(raise_exception=gateway.raise_exception)
        elif method == 'smpp':
            self.send_sms_by_smpp(raise_exception=gateway.raise_exception)
        elif method == 'ovh':
            self.send_sms_by_ovh(raise_exception=gateway.raise_exception)

    @api.one
    def send_sms(self):
        """
        Method sending SMS from the queue
        """
        if self._test_error_before_sending(self):
            method = self.gateway_id.method
            self.send_sms_by_method(method=method)
            if self.state == 'sent':
                self.env['sms.smsclient.history'].\
                    create({
                            'name': _('SMS Sent'),
                            'gateway_id': self.gateway_id.id,
                            'sms': self.msg,
                            'to': self.mobile,
                            })


class Properties(models.Model):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'

    name = fields.Char('Property name', size=256,
                       help='Name of the property whom appear on the URL')
    value = fields.Char('Property value', size=256,
                        help='Value associate on the property for the URL')
    gateway_id = fields.Many2one('sms.smsclient', 'SMS Gateway')
    type = fields.Selection([
                             ('user', 'User'),
                             ('password', 'Password'),
                             ('sender', 'Sender Name'),
                             ('to', 'Recipient No'),
                             ('sms', 'SMS Message'),
                             ('service_name', 'Service name'),
                             ('extra', 'Extra Info'),
                             ], 'API Method', select=True,
                            help="If parameter concern a value to "
                            "substitute, indicate it")


class HistoryLine(models.Model):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'

    name = fields.Char('Description', size=160, required=True, readonly=True)
    date_create = fields.Datetime('Date', readonly=True)
    user_id = fields.Many2one('res.users', 'Username',
                              readonly=True, select=True)
    gateway_id = fields.Many2one('sms.smsclient', 'SMS Gateway',
                                 ondelete='set null', required=True)
    to = fields.Char('Mobile No', size=15, readonly=True)
    sms = fields.Text('SMS', size=160, readonly=True)

    _defaults = {
                 'date_create': fields.Datetime.now(),
                 'user_id': lambda obj, cr, uid, context: uid,
                 }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        super(HistoryLine, self).create(cr, uid, vals, context=context)
        cr.commit()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
