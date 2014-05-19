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

from openerp.osv import fields, orm
from openerp import tools
from openerp.tools.translate import _

class stock_move(orm.Model):
    _inherit = 'stock.move'
    
    def _check_quantity(self, cr, uid, ids, context=None):
        for move_data in self.browse(cr, uid, ids, context=context):
            if move_data.prodlot_id.id and move_data.product_qty != 1:
                raise orm.except_orm(_('Error'), _('Serial move must have a qty equal to 1'))
                return False
            if move_data.prodlot_id.id and move_data.location_id.usage == 'internal' and move_data.state not in ('done','cancel'):
                qty = move_data.product_qty
                qty_on_hand = move_data.prodlot_id.stock_available
                res = qty_on_hand - qty
                if res < 0:
                    name = move_data.prodlot_id.name
                    raise orm.except_orm(_('Error'), _('The Prodlot %s has not enough quantity on hand (%s)') % (name,qty_on_hand))
                    return False
        return True
    
    _constraints = [
        (_check_quantity, 'Serial move must have a qty equal to 1',['prodlot_id']),
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: