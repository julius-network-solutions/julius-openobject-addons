# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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

## NOT WORKING ##

class mail_mail(orm.Model):
    _inherit = 'mail.mail'
    
    def create(self, cr, uid,values, context=None):
        print context
        print values
        new_id = super(mail_mail, self).create(cr, uid, values, context=context)
        if values['type'] == 'email':
            print new_id
            return self.email_confirmation(cr, uid, context=context)
        return new_id
    

    def email_confirmation(self, cr, uid, context=None):
        print '3'
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'email_confirmation', 'email_confirmation_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'email_confirmation', 'email_confirmation_tree')
        tree_id = tree_res and tree_res[1] or False
        print form_id
        print tree_id
        return {
            'name': _('Email Confirmation'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'mail.confirm',
#            'res_id': new_id,
            'target': 'new',
            'view_id': False,
            'views': [(form_id, 'form'),(tree_id, 'tree')],
            'type': 'ir.actions.act_window',
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
