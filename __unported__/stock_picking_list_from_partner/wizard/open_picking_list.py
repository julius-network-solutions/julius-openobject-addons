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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import time
from openerp import models, fields, api, _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT as DT,
                           DEFAULT_SERVER_DATETIME_FORMAT as DDT)
from openerp.exceptions import Warning


def date_to_datetime(date):
    return time.strftime(DDT, time.strptime(date, DT))


class open_picking_list(models.TransientModel):
    _name = 'open.picking.list'
    _description = 'Open Picking list from partner'

    partner_id = fields.Many2one('res.partner', 'Partner')
    date_from = fields.Date('Date from')
    date_to = fields.Date('Date to')
    picking_type_id = fields.Many2one('stock.picking.type', 'Type')

    @api.one
    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """
        Check if date to is greater than date from
        """
        if self.date_to and self.date_from and \
                self.date_to < self.date_from:
            raise Warning(_('Ending Date cannot be set '
                            'before Beginning Date.'))

    @api.multi
    def open_list(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_ready')
        action_read = action.read()[0]
        context = {
                   'contact_display': 'partner_address',
                   }
        partner_id = False
        if self.partner_id:
            partner_id = self.partner_id.id
        else:
            if self._context.get('active_model') == 'res.partner':
                partner_id = self._context.get('active_id')
        context.update({
                        'search_default_partner_id': partner_id,
                        })
        if self.date_from:
            context.update({
                            'search_default_date_from': self.date_from,
                            })
        if self.date_to:
            context.update({
                            'search_default_date_to': self.date_to,
                            })
        if self.picking_type_id:
            context.\
                update({
                        'search_default_picking_type_id': [self.\
                                                           picking_type_id.id],
                        'default_picking_type_id': self.picking_type_id.id,
                        })
        action_read['context'] = str(context)
        return action_read

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
