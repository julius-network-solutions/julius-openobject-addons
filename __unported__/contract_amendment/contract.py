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

from openerp import models, fields, api, _

class account_analytic_account(models.Model):
    """ Inherits the account analytic account native model
    Adds a possibility to create an amendment of this contract
    """
    _inherit = 'account.analytic.account'

    main_id = fields.Many2one('account.analytic.account', 'Main contract',
                              readonly=True)
    history_ids = fields.One2many('account.analytic.account', 'main_id',
                                  'Histories', readonly=True)

    @api.model
    def _get_default_values_for_amendment(self):
        """ Get default value to make an amendment """
        return {}

    @api.one
    def action_after_amendment(self, contract):
        """
        Inheritable action to update the amendment
        once created.
        """
        return

    @api.multi
    def make_amendment(self):
        """ Action to make an amendment """
        for contract in self:
            default = contract._get_default_values_for_amendment()
            default.update({
                            'history_ids': False,
                            'main_id': contract.id,
                            })
            old_contract = contract.copy(default)
            old_contract.name = _('%s (old %s)' %(contract.name,
                                                  contract.code))
            old_contract.action_after_amendment(contract)
            old_contract.set_close()
            

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
