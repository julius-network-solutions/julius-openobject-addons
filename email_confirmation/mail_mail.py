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

#TODO: For the moment only manual create mail are in "waiting" state , 
#      All the automatic mail creation need to be confirm before sending


class mail_mail(orm.Model):
    _inherit = 'mail.mail'
    
    _columns = {
            'state': fields.selection([('outgoing', 'Outgoing'),
                                       ('sent', 'Sent'),
                                       ('waiting', 'Waiting Confirmation'),
                                       ('received', 'Received'),
                                       ('exception', 'Delivery Failed'),
                                       ('cancel', 'Cancelled'),
                                       ], 'Status', readonly=True),
        }        

    
    def create(self, cr, uid,values, context=None):
        print context
        print values
        values.update({'state': 'waiting'})
        print values
        new_id = super(mail_mail, self).create(cr, uid, values, context=context)
        print new_id
        return new_id
    
    def confirm_mail(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids[0],{'state':'outgoing'},context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
