# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, fields, api, _


class sale_order(models.Model):
    _inherit = 'sale.order'

    stock_state = fields.\
        Selection([
                   ('no_picking', 'No Picking yet'),
                   ('draft', 'Draft'),
                   ('cancel', 'Cancelled'),
                   ('waiting', 'Waiting Another Operation'),
                   ('confirmed', 'Waiting Availability'),
                   ('partially_available', 'Partially Available'),
                   ('assigned', 'Ready to Transfer'),
                   ('done', 'Transferred'),
                   ('many', 'Many states'),
                   ], 'Stock state',
                  compute='_get_stock_state')
    stock_state_many = fields.Char('Stock state if many',
                                   compute='_get_stock_state')

    def _get_stock_state(self):
        state = 'no_picking'
        state_many = ''
        states = {}
        selection_keys = {
                          'draft': _('Draft'),
                          'cancel': _('Cancelled'),
                          'waiting': _('Waiting Another Operation'),
                          'confirmed': _('Waiting Availability'),
                          'partially_available': _('Partially Available'),
                          'assigned': _('Ready to Transfer'),
                          'done': _('Transferred'),
                          }
        if self.picking_ids:
            for picking in self.picking_ids:
                states[picking.state] = True
            if len(states.keys()) == 1:
                state = states.keys()[0]
            else:
                state = 'many'
        self.stock_state = state
        if state == 'many':
            state_many = ', '.join([selection_keys.get(x)
                                    for x in states.keys()])
        self.stock_state_many = state_many

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
