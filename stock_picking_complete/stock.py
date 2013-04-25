# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions (<http://www.julius.fr/>) contact@julius.fr
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

def _complete_check(pickings):
    res = {}
    for picking in pickings:
        res[picking.id] = False
        if picking.state == 'done':
            res[picking.id] = True
        elif picking.state == 'assigned':
            if picking.move_type == 'one':
                res[picking.id] = True
            else:
                val = True
                for move in picking.move_lines:
                    if move.state not in ('cancel','assigned','done'):
                        val = False
                        break
                res[picking.id] = val
    return res
    
class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    
    def _check_complete_picking(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        pickings = self.browse(cr, uid, ids, context=context)
        res = _complete_check(pickings)
        return res
    
    _columns = {
        'complete_picking': fields.function(_check_complete_picking, type='boolean', string='Complete')
    }
    
class stock_picking_in(orm.Model):
    _inherit = 'stock.picking.in'
    
    def _check_complete_picking(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        pickings = self.browse(cr, uid, ids, context=context)
        res = _complete_check(pickings)
        return res
    
    _columns = {
        'complete_picking': fields.function(_check_complete_picking, type='boolean', string='Complete')
    }
    
class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'
    
    def _check_complete_picking(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        pickings = self.browse(cr, uid, ids, context=context)
        res = _complete_check(pickings)
        return res
    
    _columns = {
        'complete_picking': fields.function(_check_complete_picking, type='boolean', string='Complete')
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
