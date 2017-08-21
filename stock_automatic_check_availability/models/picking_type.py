# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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


class stock_picking_type(models.Model):
    _inherit = "stock.picking.type"

    automatic_cancel_check = fields.\
        Boolean(default=False, help="If checked, the cron 'Run stock cancel "
                "then check availability scheduler', will be automatically "
                "performed on this type.")

    @api.multi
    def _run_cancel_picking_availability(self):
        """
        This method will cancel availability of linked moves
        """
        picking_obj = self.env['stock.picking']
        for type in self:
            pickings = picking_obj.\
                search([
                        ('picking_type_id', '=', type.id),
                        ('state', 'in', ['partially_available', 'assigned']),
                        ])
            pickings.do_unreserve()

    @api.multi
    def _run_check_picking_availability(self):
        """
        This method will re-check availability of linked moves
        """
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        for type in self:
            pickings = picking_obj.\
                search([
                        ('picking_type_id', '=', type.id),
                        ('state', 'in', ['waiting', 'confirmed']),
                        ])
            moves = move_obj.\
                search([
                        ('picking_id', 'in', pickings.ids),
                        ('state', 'in', ['waiting', 'confirmed']),
                        ], order='date_expected')
            moves.action_assign()

    @api.model
    def run_cancel_check_availability(self):
        """
        This action will :
            * first, cancel availability of linked moves,
            * then, check availability order by planned date.
        """
        types = self.search([
                             ('automatic_cancel_check', '=', True),
                             ])
        types._run_cancel_picking_availability()
        types._run_check_picking_availability()
        return {}
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
