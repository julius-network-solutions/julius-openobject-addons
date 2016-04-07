# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Julius Network Solutions SARL <contact@julius.fr>
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


class stock_return_picking(models.TransientModel):
    _inherit = 'stock.return.picking'

    filter_return = fields.\
        Selection([
                   ('return', 'Create a draft return'),
                   ('cancel', 'Cancel: create return and validate it'),
                   ('modify', 'Modify: create return, validate it and ' \
                    'create a new draft picking')
                   ], "Return method", required=True, default='return')

    @api.multi
    def _confirm_returns(self, picking_id):
        """
        Confirm automatically the returned picking
        """
        picking_obj = self.env['stock.picking']
        picking = picking_obj.browse(picking_id)
        picking.action_done()

    @api.multi
    def _create_draft_copy(self, picking_id):
        new_picking_id, pick_type_id = self.\
            with_context(active_id=picking_id)._create_returns()
        move_obj = self.env['stock.move']
        moves = move_obj.search([('picking_id', '=', new_picking_id)])
        for move in moves:
            move.write({
                        'location_id': move.location_dest_id.id,
                        'location_dest_id': move.location_id.id,
                        })
        return new_picking_id, pick_type_id

    @api.multi
    def create_returns(self):
        """
         Creates return picking.
         @return: A dictionary which of fields with values.
        """
        filter_return = self.filter_return or 'return'
        if filter_return in ('cancel', 'modify'):
            return_picking_id, pick_type_id = self._create_returns()
            self._confirm_returns(return_picking_id)
            if filter_return == 'cancel':
                # Override the context to disable all the potential
                # filters that could have been set previously
                ctx = {
                       'search_default_picking_type_id': pick_type_id,
                       'search_default_draft': False,
                       'search_default_assigned': False,
                       'search_default_confirmed': False,
                       'search_default_ready': False,
                       'search_default_late': False,
                       'search_default_available': False,
                       }
                domain = "[('id', 'in', [%s])]" % return_picking_id
                return {
                        'domain': domain,
                        'name': _('Returned Picking'),
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'stock.picking',
                        'type': 'ir.actions.act_window',
                        'context': ctx,
                        }
            else:
                new_picking_id, pick_type_id = self.\
                    _create_draft_copy(return_picking_id)
                ctx = {
                       'search_default_draft': False,
                       'search_default_assigned': False,
                       'search_default_confirmed': False,
                       'search_default_ready': False,
                       'search_default_late': False,
                       'search_default_available': False,
                       }
                domain = "[('id', 'in', [%s,%s])]" % (return_picking_id,
                                                      new_picking_id,)
                return {
                        'domain': domain,
                        'name': _('Returned Picking'),
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'stock.picking',
                        'type': 'ir.actions.act_window',
                        'context': ctx,
                        }
        else:
            return super(stock_return_picking, self).create_returns()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
