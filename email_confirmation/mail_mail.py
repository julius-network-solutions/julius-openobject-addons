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

class mail_message(orm.Model):
    _inherit = 'mail.message'
    
    _columns = {
        'type': fields.selection([
                        ('email', 'Email'),
                        ('comment', 'Comment'),
                        ('notification', 'System notification'),
                        ('waiting', 'Waiting Confirmation'),
                        ], 'Type',
            help="Message type: email for email message, notification for system "\
                 "message, comment for other messages such as user replies"),
        }        

    def create(self, cr, uid, values, context=None):
        values.update({'type': 'waiting'})
        return super(mail_message, self).create(cr, uid, values, context=context)
    
    def confirm_mail(self, cr, uid, ids, context=None):
        for mail_message_id in ids:
            res = self.write(cr, uid, mail_message_id, {'type':'email'}, context=context)
            self._notify(cr, uid, mail_message_id, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
