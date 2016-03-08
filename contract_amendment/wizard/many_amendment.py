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

from openerp import models, api, _
from openerp.exceptions import Warning


class account_analytic_account_amendment(models.TransientModel):
    _name = "account.analytic.account.amendment"
    _description = "Amendment for many contracts"

    @api.multi
    def make_amendment(self):
        """
        Action performed after a selection of many contracts.
        """
        contract_obj = self.env['account.analytic.account']
        contract_ids = self._context.get('active_ids')
        contracts = contract_obj.search([
                                         ('state', '=', 'open'),
                                         ('id', 'in', contract_ids),
                                         ])
        if contracts:
            contracts.make_amendment()
        else:
            raise Warning(_("There's no 'open' contract contract "
                            "in this selection. Please select 'open' "
                            "contracts to be able to set them to 'amendment'"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
