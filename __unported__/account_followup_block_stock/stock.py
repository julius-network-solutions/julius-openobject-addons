# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def onchange_partner_in(self, cr, uid,
        ids, partner_id=None, context=None):
        warning = {}
        result = super(stock_picking,
            self).onchange_partner_in(
            cr, uid, ids, partner_id=partner_id, context=context)
        warning_msgs = result.get('warning') and \
            result['warning']['message'] or ''
        warning_title = result.get('warning') and \
            result['warning']['title'] or ''
        if partner_id:
            res_partner_obj = self.pool.get('res.partner')
            partner = res_partner_obj.browse(
                cr, uid, partner_id, context=context)
            opposition = partner.latest_followup_level_id
            if not opposition and partner.parent_id:
                opposition = partner.parent_id.latest_followup_level_id
            if opposition:
                if not warning_title:
                    warning_title = _('Warning!')
                warn_msg = (_("This customer has got a follow up:"
                                 " %s\n") %opposition.name)
                if opposition.block_sale:
                    warn_msg += _("You will not be able to confirm "
                                  "this Picking if you're not in "
                                  "the accounting department")
                else:
                   warn_msg += _("But, this follow up will not block the "
                                 "confirmation of this picking")
                warning_msgs += warn_msg
        if warning_msgs:
            warning = {
               'title': warning_title,
               'message' : warning_msgs,
            }
            result.update({'warning': warning})
        return result

    def _check_partner_followup(self, cr, uid, partner_id, context=None):
        opposition = partner_id and \
            (partner_id.latest_followup_level_id and \
            partner_id.latest_followup_level_id.block_stock and 
            partner_id.latest_followup_level_id) or \
            (partner_id.parent_id and \
            partner_id.parent_id.latest_followup_level_id and \
            partner_id.parent_id.latest_followup_level_id.block_stock and \
            partner_id.parent_id.latest_followup_level_id)
        manager = self.user_has_groups(cr, uid,
            'account_followup_block_stock.group_stock_followup_manager', context=context)
        if opposition and not manager:
            raise orm.except_orm(_('Warning!'),
                _('You cannot confirm a picking for a customer '
                  'with follow up %s.\nAsk one of the accounting manager '
                  'to confirm this picking.')
                % (opposition.name))

    def action_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for stock in self.browse(cr, uid, ids, context=context):
            partner_id = stock.partner_id
            if partner_id:
                self._check_partner_followup(cr, uid, partner_id, context=context)
        return super(stock_picking,
            self).action_process(cr, uid, ids, context=context)


class stock_picking_in(stock_picking):
    _name = 'stock.picking.in'
    _inherit = 'stock.picking.in'

class stock_picking_out(stock_picking):
    _name = 'stock.picking.out'
    _inherit = 'stock.picking.out'
    
class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _check_partner_followup(self, cr, uid, partner_id, context=None):
        opposition = partner_id and \
            (partner_id.latest_followup_level_id and \
            partner_id.latest_followup_level_id.block_stock and 
            partner_id.latest_followup_level_id) or \
            (partner_id.parent_id and \
            partner_id.parent_id.latest_followup_level_id and \
            partner_id.parent_id.latest_followup_level_id.block_stock and \
            partner_id.parent_id.latest_followup_level_id)
        manager = self.user_has_groups(cr, uid,
            'account_followup_block_stock.group_stock_followup_manager', context=context)
        if opposition and not manager:
            raise orm.except_orm(_('Warning!'),
                _('You cannot confirm a move for a customer '
                  'with follow up %s.\nAsk one of the accounting manager '
                  'to confirm this move.')
                % (opposition.name))

    def action_partial_move(self, cr, uid, ids, context=None):
        if context is None: context = {}
        for stock in self.browse(cr, uid, ids, context=context):
            partner_id = stock.partner_id or \
                stock.picking_id.partner_id or False
            if partner_id:
                self._check_partner_followup(cr, uid, partner_id, context=context)
        return super(stock_move,
            self).action_partial_move(cr, uid, ids, context=context)

    def action_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for stock in self.browse(cr, uid, ids, context=context):
            partner_id = stock.partner_id or \
                stock.picking_id.partner_id or False
            if partner_id:
                self._check_partner_followup(cr, uid, partner_id, context=context)
        return super(stock_move,
            self).action_done(cr, uid, ids, context=context)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: