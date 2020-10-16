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

from openerp import fields, models, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    picking_count = fields.Integer("# of Picking", compute="_picking_count")
    picking_ids = fields.One2many('stock.picking', 'partner_id', 'Pickings')

    @api.one
    def _picking_count(self):
        try:
            self.picking_count = len(self.picking_ids) + \
                len(self.mapped('child_ids.picking_ids'))
        except:
            pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
