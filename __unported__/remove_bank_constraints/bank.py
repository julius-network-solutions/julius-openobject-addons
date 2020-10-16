# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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

class res_partner_bank(orm.Model):
    _inherit = "res.partner.bank"
    
    def _check_key(self, cr, uid, ids):
        return True
    
    def check_iban(self, cr, uid, ids, context=None):
        return True
    
    def _check_bank(self, cr, uid, ids, context=None):
        return True

    def _construct_constraint_msg(self, cr, uid, ids, context=None):
        return _('The IBAN is invalid, it should begin with the country code'), ()
    
    _constraints = [
        (_check_key, 'The RIB and/or IBAN is not valid', ['rib_acc_number', 'bank_code', 'office', 'key']),
        (check_iban, _construct_constraint_msg, ["iban"]),
        (_check_bank, '\nPlease define BIC/Swift code on bank for bank type IBAN Account to make valid payments', ['bic']),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: