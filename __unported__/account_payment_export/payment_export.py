# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

#import time
from openerp.osv import orm, fields
#import netsvc
#import pooler

class account_pay(orm.Model):
    _name = "account.pay"
    _description = "Payment Export History"
    _rec_name = 'payment_order_id'
    _columns = {
        'payment_order_id': fields.many2one('payment.order', 'Payment Order Reference',readonly=True),
        'state': fields.selection([('failed','Failed'),('succeeded', 'Succeeded')],'Status',readonly=True),
        'file': fields.binary('Saved File', readonly=True),
        'note': fields.text('Creation Log', readonly=True),
        'create_date': fields.datetime('Creation Date',required=True, readonly=True),
        'create_uid': fields.many2one('res.users', 'Creation User', required=True, readonly=True),
    }

class res_partner_bank(orm.Model):
    _inherit = "res.partner.bank"
    _columns = {
        'institution_code':fields.char('Institution Code', size=3), 
    }

class res_bank(orm.Model):
    _inherit = "res.bank"

    _columns = {
        'bilateral':fields.char('Bilateral Relationship', size=12, help="This field may contain indications on the processing to be applied, e.g. an indication concerning the globalisation of these payments.The content of this field must be laid down on a bilateral basis between the bank and its client."),
    }

class payment_method(orm.Model):
    _name="payment.method"
    _description="Payment Method For Export"

    _columns = {
        'name': fields.char('Code',size=3,required=True),
        'description': fields.text('Description'),
    }

class charges_code(orm.Model):
    _name="charges.code"
    _description="Charges Codes For Export"

    _columns = {
        'name': fields.char('Code',size=3,required=True),
        'description': fields.text('Description'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
