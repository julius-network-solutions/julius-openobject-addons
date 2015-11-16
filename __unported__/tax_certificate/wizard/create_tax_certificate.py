# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

import openerp.pooler
from openerp import models, fields, api, _

class create_tax_certificate(models.TransientModel):
    _name = 'create.tax.certificate'
    _description = 'Tax certificate creation'

    fiscalyear_id = fields.Many2one('account.fiscalyear',
                                    'Fiscal Year', required=True)
    filter = fields.Selection([
                               ('no_one', 'No Filters'),
                               ('date', 'By dates'),
                               ('period', 'By period'),
                               ('both', 'By date and by period'),
                               ], 'Date/period chosen', required=True,
                              default='no_one')
    date_begin = fields.Date('Begin Date')
    date_end = fields.Date('End Date')
    period_ids = fields.Many2many('account.period', 'certificate_wizard_rel',
                                  'period_id', 'memory_id', 'Periods')
    partner_ids = fields.Many2many('res.partner',
                                   'certificate_wizard_partner_rel',
                                   'partner_id', 'memory_id', 'Partners')

    @api.onchange('fiscalyear_id', 'filter')
    def onchange_fiscal_filter(self):
        if not self.fiscalyear_id:
            self.date_begin = False
            self.date_end = False
            self.period_ids = []
        else:
            if self.filter and self.filter != 'no_one':
                if self.filter in ['date', 'both']:
                    self.date_begin = self.fiscalyear_id.date_start
                    self.date_end = self.fiscalyear_id.date_stop
                if self.filter in ['period', 'both']:
                    self.period_ids = self.fiscalyear_id.period_ids
        
    _defaults = {
        'partner_ids': lambda self, cr, uid, ctx: ctx.get('active_ids', []),
    }

    @api.multi
    def create_certificate(self):
        for rec in self:
            invoice_obj = self.env['account.invoice']
            domain = [('state', 'not in', ['draft', 'cancel'])]
            period_ids = []
            filter = rec.filter
            if filter in ['period', 'both']:
                period_ids = rec.period_ids.ids
            else:
                period_ids = rec.fiscalyear_id.period_ids.ids
            domain.append(
                ('period_id', 'in', period_ids),
            )
            if rec.partner_ids:
                partner_ids = rec.partner_ids.ids
                domain += [
                    '|', ('partner_id', 'in', partner_ids),
                    ('partner_id.parent_id', 'in', partner_ids)
                ]
            if filter in ['date','both']:
                domain.append(
                    ('date_invoice', '>=', rec.date_begin)
                )
                domain.append(
                    ('date_invoice', '<=', rec.date_end)
                )
            invoices = invoice_obj.search(domain)
            fiscalyear = rec.fiscalyear_id
            certificates = invoices.create_certificate(fiscalyear,
                                                       product_ids=[])
            act = self.env.ref('tax_certificate.action_tax_certificate_list')
            action = act.read()
            if isinstance(action, list):
                action = action and action[0] or {}
            action['domain'] = [('id', 'in', certificates.ids)]
            return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
