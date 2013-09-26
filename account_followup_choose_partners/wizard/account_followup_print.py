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

class account_followup_print_select_validate(orm.TransientModel):
    _name = 'account_followup.print.select.validate'
    _descrition = 'Validate Follow Ups'

    def do_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids')
        select_obj = self.pool.get('account_followup.print.select')
        return select_obj.do_process(cr, uid, active_ids, context=context)

class account_followup_print_select(orm.TransientModel):
    _name = 'account_followup.print.select'
    _description = 'Select Customers to Print Follow-up & Send Mail to Customers'
    _columns = {
        'name': fields.char('Name', size=128),
        'partner_id': fields.many2one('res.partner', 'Partner',
                                      required=True, readonly=True),
        'move_line_id': fields.many2one('account.move.line',
                                        'Move line',
                                        required=True, readonly=True),
        'level': fields.many2one('account_followup.followup.line',
                                 'Follow Up Level',
                                 required=True, readonly=True),
        'followup_print_id': fields.many2one('account_followup.print',
                                             'Follow Up Level',
                                             readonly=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done')
            ], 'State', required=True),
    }

    _defaults = {
            'state': 'draft'
        }

    def do_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        partner_list = []
        to_update = {}
        followup_print_ids = []
        parent_obj = self.pool.get('account_followup.print')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(
            cr, uid, uid, context=context).company_id.id
        for current in self.browse(cr, uid, ids, context=context):
            if current.state == 'done':
                continue
            partner_id = current.partner_id.id * 10000 + company_id
            if partner_id not in partner_list:
                partner_list.append(partner_id)
            to_update[str(current.move_line_id.id)] = {
                'level': current.level.id,
                'partner_id': partner_id,
                }
            if current.followup_print_id.id not in followup_print_ids:
                followup_print_ids.append(current.followup_print_id.id)
        date = parent_obj.browse(cr, uid,
                                 followup_print_ids, context=context)[0].date
        data = parent_obj.read(cr, uid,
                               followup_print_ids, [], context=context)[0]
        data['followup_id'] = data['followup_id'][0]

        #Update partners
        parent_obj.do_update_followup_level(cr, uid,
                                            to_update, partner_list,
                                            date, context=context)
        #process the partners (send mails...)
        restot = parent_obj.process_partners(cr, uid,
                                             partner_list, data,
                                             context=context)
        #clear the manual actions if nothing is due anymore
        nbactionscleared = parent_obj.clear_manual_actions(
            cr, uid, partner_list, context=context)
        if nbactionscleared > 0:
            restot['resulttext'] = restot['resulttext'] + "<li>" + \
                _("%s partners have no credits and as such the action is cleared") \
                %(str(nbactionscleared)) + "</li>" 
        res = restot['action']

        #return the next action
        mod_obj = self.pool.get('ir.model.data')
        model_data_ids = mod_obj.search(cr, uid, [
            ('model','=','ir.ui.view'),
            ('name','=','view_account_followup_sending_results')
            ], context=context)
        resource_id = mod_obj.read(cr, uid,
            model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        context.update({
                        'description': restot['resulttext'],
                        'needprinting': restot['needprinting'],
                        'report_data': res
                        })
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return {
            'name': _('Send Letters and Emails: Actions Summary'),
            'view_type': 'form',
            'context': context,
            'view_mode': 'tree,form',
            'res_model': 'account_followup.sending.results',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

class account_followup_print(orm.TransientModel):
    _inherit = 'account_followup.print'
    _description = 'Print Follow-up & Send Mail to Customers'
    
    def do_process2(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        company_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id
        select_obj = self.pool.get('account_followup.print.select')
        #Get partners
        tmp = self._get_partners_followp(cr, uid, ids, context=context)
        to_update = tmp['to_update']
        followup_print_id = ids[0]
        select_ids = []
        for key in to_update.keys():
            partner_id = to_update[key].get('partner_id')
            if not partner_id:
                continue
            partner_id = (partner_id - company_id) / 10000
            level = to_update[key].get('level')
            move_line_id = int(key)
            vals = {
                'partner_id': partner_id,
                'level': level,
                'move_line_id': move_line_id,
                'followup_print_id': followup_print_id,
                }
            select_ids.append(select_obj.create(cr, uid,
                                                vals, context=context))
        mod_obj = self.pool.get('ir.model.data')
        action_model, action_id = mod_obj.get_object_reference(cr, uid,
            'account_followup_choose_partners',
            'action_account_followup_sending_partner_list')
        
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            if select_ids:
                action['domain'] = "[('id','in', [" + \
                    ','.join(map(str,select_ids))+"])]"
            else:
                action['domain'] = "[('id','in', [0])]"
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
