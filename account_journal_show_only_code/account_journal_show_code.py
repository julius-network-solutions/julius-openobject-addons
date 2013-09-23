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

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _

class account_journal(orm.Model):
    
    _inherit = 'account.journal'
   
    def name_get(self, cr, user, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = self.browse(cr, user, ids, context=context)
        res = []
        for rs in result:
#             currency = False
#             if rs.currency:
#                 currency = rs.currency
#             else:
#                 currency = rs.company_id.currency_id
            name = "%s" % (rs.code)
#             if currency:
#                 name += " (%s)" % (currency.name,)
            res += [(rs.id, name)]
        return res

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
