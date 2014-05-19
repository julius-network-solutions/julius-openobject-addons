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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class mail_message(orm.Model):
    _inherit = 'mail.message'
    
    def create(self, cr, uid,values, context=None):
        model = values.get('model')
        obj_model = self.pool.get(model)
        res_id = values.get('res_id')
        if obj_model and res_id:
            obj = obj_model.browse(cr,uid,res_id,context=context)
            if model in ('crm.phonecall','sale.order','crm.lead','crm.meeting'):
                partner_id = obj.user_id.partner_id.id
                partner_ids = values.get('notified_partner_ids')
                if partner_ids:
                    partner_ids = partner_ids[0][2]
                    partner_ids.append(partner_id)
                else:
                    partner_ids = [partner_id]
                values.update({'notified_partner_ids': [(6,0,partner_ids)]})
        new_id = super(mail_message, self).create(cr, uid, values, context=context)
        return new_id

        
#        message = self.browse(cr,uid,new_id,context=context)
#        model = message.model
#        res_id = message.res_id 
#        obj_model = self.pool.get(model)
#        obj = obj_model.browse(cr,uid,res_id,context=context)
#        user_id = obj.user_id.partner_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: