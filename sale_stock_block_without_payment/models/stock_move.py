# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    Copyright (C) 2015: Ursa Information Systems
#    Author: Sandip Mangukiya (<smangukiya@ursainfosystems.com>)
#    Website:(<http://www.ursainfosystems.com>).
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

from openerp import fields, models
from openerp.tools.translate import _
from openerp import api
from openerp.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_order_blocked(self):
        blocked = False
        if (self.picking_id.sale_order_blocked) or \
                (self.picking_id.sale_id and
                 self.picking_id.sale_id.block_without_payment and not
                 self.picking_id.sale_id.marked_as_paid):
            blocked = True
        self.sale_order_blocked = blocked

    sale_order_blocked = fields.Boolean(compute=_get_order_blocked,
                                        string='Sale order blocked',
                                        store=False)

    @api.v7
    def action_done(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if move.sale_order_blocked:
                sale_order_name = move.picking_id and move.picking_id.sale_id\
                                  and move.picking_id.sale_id.name or ''
                raise ValidationError(_('You can\'t validate this move because'
                                        ' the sale order %s hasn\'t been '
                                        'paid.') % sale_order_name)
        return super(StockMove, self).action_done(cr, uid, ids,
                                                  context=context)

    @api.v8
    def action_done(self):
        if self.sale_order_blocked:
            sale_order_name = self.picking_id and self.picking_id.sale_id\
                              and self.picking_id.sale_id.name or ''
            raise ValidationError(_('You can\'t validate this move because the'
                                    ' sale order %s hasn\'t been paid.')
                                  % sale_order_name)
        return super(StockMove, self).action_done()
