# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import fields, models, api, _


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _scrap_reason_get(self):
        reasons = self.env['stock.move.scrap.reason'].search([])
        result = []
        for reason in reasons:
            result.append((reason.id, reason.name))

        result.append((-1, 'Other...'))
        return result

    reason = fields.Selection(_scrap_reason_get, help="Reason for scraping.")
    notes_reason = fields.Text('Notes')

    def action_scrap(self, cr, uid, ids, quantity, location_id,
                     restrict_lot_id=False, restrict_partner_id=False,
                     context=None):
        """ Move the scrap/damaged product into scrap location
        @param cr: the database cursor
        @param uid: the user id
        @param ids: ids of stock move object to be scrapped
        @param quantity : specify scrap qty
        @param location_id : specify scrap location
        @param context: context arguments
        @return: Scraped lines
        """
        res = super(stock_move, self).\
            action_scrap(cr, uid, ids, quantity,
                         location_id=location_id,
                         restrict_lot_id=restrict_lot_id,
                         restrict_partner_id=restrict_partner_id,
                         context=context)[0]
        if context.get('reason'):
            reason = context.get('reason')
            notes_reason = context.get('notes_reason') or False
            self.write(cr, uid, res, {
                                      'reason': int(reason),
                                      'notes_reason': notes_reason,
                                      }, context=context)
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
