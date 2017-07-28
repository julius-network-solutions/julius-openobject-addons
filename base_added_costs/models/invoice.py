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
from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    _order = 'id'
    
    is_cost_line = fields.Boolean(compute='_get_is_cost_line')

    @api.one
    def _get_is_cost_line(self):
        """
        Compute method for the field is_cost_line
        """
        self.is_cost_line = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
