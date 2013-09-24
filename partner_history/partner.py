# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

from osv import fields, orm
from tools.translate import _
from openerp.tools import ustr

class mail_message(orm.Model):
    _inherit = 'mail.message'

    def compute_partner(self, cr, uid, active_model='res.partner', model='mail.message', res_id=1, context=None):
        if context is None:
            context = {}
        target_ids = []
        current_obj = self.pool.get(model)
        cr.execute("SELECT name FROM ir_model_fields WHERE relation='" + active_model + "' and model = '" + model + "' and ttype not in ('many2many', 'one2many');")
        for name in cr.fetchall():
            current_data = current_obj.read(cr, uid, res_id, [str(name[0])],context=context)
            if current_data.get(str(name[0])):
                var = current_data.get(str(name[0]))
                if var:
                    target_ids.append(var[0])
                    
        cr.execute("select name, model from ir_model_fields where relation='" + model + "' and ttype in ('many2many') and model = '" + active_model + "';")
        for field, model in cr.fetchall():
            field_data = self.pool.get(model) and self.pool.get(model)._columns.get(field, False) \
                            and (isinstance(self.pool.get(model)._columns[field], fields.many2many) \
                            or isinstance(self.pool.get(model)._columns[field], fields.function) \
                            and self.pool.get(model)._columns[field].store) \
                            and self.pool.get(model)._columns[field] \
                            or False
            if field_data:
                model_m2m, rel1, rel2 = field_data._sql_names(self.pool.get(model))
                requete = "SELECT "+rel1+" FROM "+ model_m2m+" WHERE "+ rel2+" ="+str(res_id)+";"
                cr.execute(requete)
                sec_target_ids = cr.fetchall()
                for sec_target_id in sec_target_ids:
                    target_ids.append(sec_target_id[0])
        return target_ids
    
    def _get_object_name(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        model_obj = self.pool.get('ir.model')
        for message in self.browse(cr, uid, ids, context=context):
            model_ids = model_obj.search(cr, uid, [('model','=',message.model)], limit=1)
            if model_ids:
                model_name = model_obj.browse(cr, uid, model_ids[0], context=context).name
                result[message.id] = model_name
        return result
    
    def _get_body_txt(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for message in self.browse(cr, uid, ids, context=context):
            if message.res_id:
                record_data = self.pool.get(message.model).browse(cr, uid, message.res_id, context=context)
                if message.model == 'crm.phonecall':
                    body_txt = record_data.name
                elif message.model == 'crm.meeting' or message.model == 'crm.lead':
                    body_txt = record_data.description
                else:
                    body_txt = record_data.name
                result[message.id] = body_txt
        return result
    
    _columns = {
        'partner_ids': fields.many2many('res.partner', 'message_partner_rel', 'message_id', 'partner_id', 'Partners'),
        'object_name': fields.function(_get_object_name, type='char', string='Object Name', size=64, store=True),
        'body_txt': fields.function(_get_body_txt, type='text', string='Content', store=True),
    }
    
    _order= 'date desc'
    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('partner_ids'):
            target_ids = []
            if vals.get('res_id') and vals.get('model'):
                target_ids = self.compute_partner(cr, uid, active_model='res.partner', model=vals.get('model'), res_id=vals.get('res_id'), context=context)
                target_ids = list(set(target_ids))
            vals.update({'partner_ids': [(6, 0, target_ids)],})
        return super(mail_message, self).create(cr, uid, vals, context=context)

class res_partner(orm.Model):
    _inherit = 'res.partner'
    
    def _get_message(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        message_obj = self.pool.get('mail.message')
        for partner in self.browse(cr, uid, ids, context=context):
            target_ids = message_obj.search(cr, uid, [
                    '|',('partner_ids', 'in', partner.id),
                    '&',('model', '=', 'res.partner'),('res_id','=',partner.id)
                ], order='date desc', context=context)
            result[partner.id] = target_ids
        return result
    
    _columns = {
        # History follow-up #
        'history_ids': fields.function(_get_message, type='many2many', relation="mail.message", string="Related Messages"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
