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

from osv import fields, orm
from openerp.tools.translate import _

class product_name_change(orm.TransientModel):
    _name = "product.translate.name"
    _columns = {
            'name_trans': fields.char('Name', size=64),
    }
    
    def change_name(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context_copy = context.copy()
        prod_id = context.get('active_id')
        prod_obj = self.pool.get('product.product')
        for this in self.browse(cr, uid, ids, context=context):
            name_trans = this.name_trans
        if name_trans:
            prod_obj.write(cr, uid, prod_id, {'name': name_trans}, context={'lang':'fr_FR'})
        return {'type': 'ir.actions.act_window_close'}
        


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
