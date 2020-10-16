# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

import datetime
import time

from openerp import tools
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _


class Do_followup_wizard(osv.TransientModel):
    _name = 'do_followup.wizard'
    _columns={
            'company_id'  : fields.many2one('res.company', 'Company'),
            'partner_ids' : fields.one2many('do_followup.wizard_list', 'partner_id','Partner List'),
            }

    def do_followup(self, cr, uid, ids, context=None):
        val = []
        if context is None:
            context = {}

        wizard_followup_line = self.browse(cr, uid, ids[0], context=context)
        for f_line in wizard_followup_line.partner_ids:
            val.append(f_line.partner.id*10000+1)

        followup_ids = self.pool.get('account_followup.followup').search(cr, uid, [('company_id', '=',wizard_followup_line.company_id.id )], context=context)

        data = {
                'date': fields.date.today(),
                'followup_id': followup_ids[0],
                'partner_ids': val,
                }
        datas = {
                    'ids': val,
                    'model': 'account_followup.followup',
                    'form': data
                }

        return {'type': 'ir.actions.report.xml', 'report_name': 'account_followup.report_followup', 'datas': datas}

    def default_get(self, cr, uid ,fields, context):
        '''fonction qui populate le wizard de production afin de
        selectionner que celle qui sont en etat 'no_produce'''''
        partner_obj = self.pool.get('res.partner')
        res = {}
        new_values = []
        active_ids = context.get('active_ids', [])
        print context

        company_id = self.pool.get('res.users').read(cr,uid,uid,['company_id'],)['company_id'][0]

        print company_id

        for partner in partner_obj.browse(cr,uid,active_ids,context):
            new_values.append((0,0,{'partner':partner.id}))
        res.update({'partner_ids': new_values,
                    'company_id' : company_id,})

        return res


class Do_followup_wizard_list(osv.TransientModel):
    _name = 'do_followup.wizard_list'
    _columns={
            'partner_id' : fields.many2one('do_followup.wizard', 'partner_id' ),
            'partner' : fields.many2one('res.partner', 'Partner', required=True),
    }
