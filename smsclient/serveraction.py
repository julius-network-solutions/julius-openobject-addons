# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
##############################################################################

from openerp.osv import orm, fields
import time
import logging
import re

_logger = logging.getLogger('smsclient')

class actions_server(orm.Model):
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
    _inherit = 'ir.actions.server'


    def _get_states(self, cr, uid, context=None):
        res = super(actions_server, self)._get_states(cr, uid, context=context)
        res.insert(0, ('sms', 'SMS'))
        return res

    _columns = {
        'mobile': fields.char('Mobile No', size=512, help="Provides fields that be used to fetch the mobile number, e.g. you select the invoice, then `object.invoice_address_id.mobile` is the field which gives the correct mobile number"),
        'sms_template_id': fields.many2one('email.template', 'SMS Template',
            help='Select the SMS Template configuration to use with this action'),
    }
    ## Function ##
    def run(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        act_ids = []
        for action in self.browse(cr, uid, ids, context=context):
            obj_pool = self.pool.get(action.model_id.model)
            obj = obj_pool.browse(cr, uid, context['active_id'], context=context)
            email_template_obj = self.pool.get('email.template')
            cxt = {
                'context': context,
                'object': obj,
                'time': time,
                'cr': cr,
                'pool': self.pool,
                'uid': uid
            }
            expr = eval(str(action.condition), cxt)
            if not expr:
                continue
            if action.state == 'sms':
                sms_pool = self.pool.get('sms.smsclient')
                queue_obj = self.pool.get('sms.smsclient.queue')
                mobile = str(action.mobile)
                to = None
                try:
                    gateway = action.sms_template_id.gateway_id
                    if mobile:
                        to = eval(action.mobile, cxt)
                    else:
                        _logger.error('Mobile number not specified !')
                    res_id = context['active_id']
                    template = email_template_obj.get_email_template(cr, uid, action.sms_template_id.id, res_id, context)
                    values = {}
                    for field in ['subject', 'body_html', 'email_from',
                                  'email_to', 'email_cc', 'reply_to']:
                        values[field] = email_template_obj.render_template(cr, uid, getattr(template, field),
                                                             template.model, res_id, context=context) \
                                                             or False
                    if values['body_html']:
                        p = re.compile(r'<.*?>')
                        text = p.sub('', values['body_html'])
                    else:
                        _logger.error('Text not specified !')
                    
                    vals ={
                        'name': gateway.url,
                        'gateway_id': gateway.id,
                        'state': 'draft',
                        'mobile': to,
                        'msg': text,
                        'validity': gateway.validity, 
                        'classes': gateway.classes, 
                        'deferred': gateway.deferred, 
                        'priority': gateway.priority, 
                        'coding': gateway.coding,
                        'tag': gateway.tag, 
                        'nostop': gateway.nostop,
                    }
                    sms_in_q = queue_obj.search(cr, uid,[
                        ('name','=',gateway.url),
                        ('gateway_id','=',gateway.id),
                        ('state','=','draft'),
                        ('mobile','=',to),
                        ('msg','=',text),
                        ('validity','=',gateway.validity), 
                        ('classes','=',gateway.classes), 
                        ('deferred','=',gateway.deferred), 
                        ('priority','=',gateway.priority), 
                        ('coding','=',gateway.coding),
                        ('tag','=',gateway.tag), 
                        ('nostop','=',gateway.nostop)
                        ])
                    if not sms_in_q:
                        queue_obj.create(cr, uid, vals, context=context)
                        _logger.info('SMS successfully send to : %s' % (to))
                except Exception, e:
                    _logger.error('Failed to send SMS : %s' % repr(e))
            else:
                act_ids.append(action.id)
        if act_ids:
            return super(actions_server, self).run(cr, uid, act_ids, context=context)
        return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
