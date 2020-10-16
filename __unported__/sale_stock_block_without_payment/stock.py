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
from openerp import netsvc
from openerp.tools.translate import _

class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _get_order_blocked(self, cr, uid, ids, name, arg=None, context=None):
        if context is None:
            context = {}
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            blocked = False
            if picking.sale_id and picking.sale_id.block_without_payment \
                and not picking.sale_id.marked_as_paid:
                blocked = True
            res[picking.id] = blocked
        return res

    _columns = {
        'sale_order_blocked': fields.function(_get_order_blocked,
            string='Sale order blocked', type='boolean', store=False),
    }

class stock_picking_out(orm.Model):
    _inherit = "stock.picking.out"

    def _get_order_blocked(self, cr, uid, ids, name, arg=None, context=None):
        if context is None:
            context = {}
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            blocked = False
            if picking.sale_id and picking.sale_id.block_without_payment \
                and not picking.sale_id.marked_as_paid:
                blocked = True
            res[picking.id] = blocked
        return res

    _columns = {
        'sale_order_blocked': fields.function(_get_order_blocked,
            string='Sale order blocked', type='boolean', store=False),
    }

class stock_move(orm.Model):
    _inherit = "stock.move"

    def _get_order_blocked(self, cr, uid, ids, name, arg=None, context=None):
        if context is None:
            context = {}
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            blocked = False
            if (move.picking_id.sale_order_blocked) or \
                (move.sale_line_id and move.sale_line_id.order_id and \
                move.sale_line_id.order_id.block_without_payment and \
                not move.picking_id.sale_id.marked_as_paid):
                blocked = True
            res[move.id] = blocked
        return res

    _columns = {
        'sale_order_blocked': fields.function(_get_order_blocked,
            string='Sale order blocked', type='boolean', store=False),
    }

    def action_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.sale_order_blocked:
                sale_order_name = move.sale_line_id and move.sale_line_id.order_id and \
                    move.sale_line_id.order_id.name or move.picking_id and \
                    move.picking_id.sale_id and move.picking_id.sale_id.name or ''
                raise orm.except_orm(_('Operation not allowed!'),
                                     _('You can\'t validate this move because the sale order '\
                                       '%s hasn\'t been paid.') %sale_order_name)
        return super(stock_move, self).action_done(cr, uid, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
