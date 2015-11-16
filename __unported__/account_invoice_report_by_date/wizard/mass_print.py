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

class mass_invoice_report(models.TransientModel):
    _name = 'mass.invoice.report'
    _description = 'Mass Invoice Report'

    journal_id = fields.Many2one('account.journal', string='Journal',
                                 required=True)
    
    date_start = fields.Date('Date Start', required=True)
    date_end = fields.Date('Date End ', required=True)

    @api.multi
    def mass_invoice(self):
        domain = [
                  ('date_invoice','>=',self.date_start),
                  ('date_invoice','<=',self.date_end),
                  ('journal_id','=',self.journal_id.id)
                  ]
        invoices = self.env['account.invoice'].search(domain)
        return self.env['report'].get_action(invoices,
                                             'account.report_invoice')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
