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

from openerp import api, models, fields
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT

class operation_cycle(models.TransientModel):
    _name = 'operation.cycle.wizard'
    _description = 'Operation Cycle Wizard'
    
    @api.multi
    def update_cycle(self):
        self.env['operation.cycle'].cycle_reorder(self._context.get('active_ids'))
        return {'type': 'ir.actions.act_window_close'}
    
class operation_cycle(models.Model):
    _inherit = 'operation.cycle'
    _description = 'Operation Cycle'
    
    @api.model
    def get_first_date(self, ids):
        date = False
        cycle_ids = self.search([('id','in',ids)], order='date_planned', limit=1)
        if cycle_ids:
            for cycle in cycle_ids:
                date = cycle.date_planned
        return date
     
    @api.model
    def cycle_reorder(self, ids):
        date = self.get_first_date(ids)
        cycles = self.browse(ids)
        for c in cycles:
            c.write({'date_planned': date})
            date = self.compute_cycle_date(date, c.hour)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: