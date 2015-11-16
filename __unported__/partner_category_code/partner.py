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
from openerp.osv import fields, orm
from openerp.tools.translate import _

class res_partner_category(orm.Model):
    _inherit = 'res.partner.category'

    def name_search(self, cr, uid, name,
                    args=None, operator='ilike',
                    context=None, limit=100):
        res = super(res_partner_category,
            self).name_search(cr, uid, name, args=args,
                              operator=operator, context=context,
                              limit=limit)
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            ids = self.search(cr, uid, [('code', 'ilike', name)]+ args, limit=limit)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)]+ args, limit=limit)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    _columns = {
        'code': fields.char('Code', size=64),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
