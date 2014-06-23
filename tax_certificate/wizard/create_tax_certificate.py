# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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
##############################################################################


from openerp.osv import fields, osv
from openerp import tools
import time
import datetime
import openerp.pooler
from openerp.tools.translate import _

class create_tax_certificate(osv.osv_memory) :
    
    _name = 'create.tax.certificate'

    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True),
        'filter' : fields.selection([
                                   ('no_one','No Filters'),
                                   ('date','By dates'),
                                   ('period','By period'),
                                   ('both','By date and by period'),
                                   ],'Date/period chosen', required=True),
        'date_begin' : fields.date('Begin Date'),
        'date_end' : fields.date('End Date'),
        'period_ids' : fields.many2many('account.period', 'certificate_wizard_rel', 'period_id', 'memory_id', 'Periods'),
        'partner_ids' : fields.many2many('res.partner', 'certificate_wizard_partner_rel', 'partner_id', 'memory_id', 'Partners'),
    }

    def on_change_fiscal_filter(self, cr, uid, id, fiscal = None, filter = None):
        date_begin = False
        date_end = False
        period_ids = []
        if not fiscal:
            return {'value' : {'date_begin' : date_begin, 'date_end' : date_end, 'period_ids' : period_ids}}
        
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        if filter and filter <> 'no_one':
            fiscal_data = fiscalyear_obj.read(cr, uid, fiscal, ['date_start','date_stop','period_ids'])
            if filter in ['date','both']:
                date_begin = fiscal_data['date_start']
                date_end = fiscal_data['date_stop']
            if filter in ['period','both']:
                period_ids = fiscal_data['period_ids']

        return {'value' : {'date_begin' : date_begin, 'date_end' : date_end, 'period_ids' : period_ids}}

    _defaults = {
        'filter': lambda *a: 'no_one',
        'partner_ids': lambda self ,cr, uid, ctx: ctx.get('active_ids', []),
    }
    
    def action_cancel(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def create_certificate(self, cr, uid, ids, context=None):
        certificate_ids = []
        pool = pooler.get_pool(cr.dbname)
        invoice_obj = pool.get('account.invoice')
        certificate_obj = pool.get('tax.certificate')
        data = self.browse(cr, uid, ids)[0]
        domain = [('state', 'not in', ['draft', 'cancel'])]
        period_ids = []
        filt = data.filter
        if filt in ['period','both']:
            periods = data.period_ids
        else:
            periods = data.fiscalyear_id.period_ids
        period_ids = [x.id for x in periods]
            
        domain.append(
            ('period_id', 'in', period_ids),
        )
        if data.partner_ids:
            partner_ids = [x.id for x in data.partner_ids]
            domain.append(
                ('partner_id', 'in', partner_ids)
            )
        if filt in ['date','both']:
            domain.append(
                ('date_invoice','>=',data.date_begin)
            )
            domain.append(
                ('date_invoice','<=',data.date_end)
            )
        
        invoice_ids = invoice_obj.search(cr, uid, domain)
        fiscalyear = data.fiscalyear_id
        certificate_ids = certificate_obj.create_certificate(cr, uid, invoice_ids, fiscalyear, product_ids=[], context=context)
        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')
        model_id = mod_obj.search(cr, uid,[('name','=','action_tax_certificate_list')])[0]
        act_id = mod_obj.read(cr, uid, model_id, ['res_id'])['res_id']
        act = act_obj.read(cr, uid, act_id)
        act['domain'] = [('id', 'in', certificate_ids)]
        return act

create_tax_certificate()