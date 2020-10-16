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

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
        date_invoice=False, payment_term=False, partner_bank_id=False,
        company_id=False, context=None):
        if context is None:
            context = {}
        warning = {}
        result = super(account_invoice,
            self).onchange_partner_id(cr, uid, ids, type, partner_id,\
            date_invoice=date_invoice, payment_term=payment_term,\
            partner_bank_id=partner_bank_id, company_id=company_id)
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
                                  "this invoice if you're not in "
                                  "the accounting department")
                else:
                   warn_msg += _("But, this follow up will not block the "
                                 "confirmation of this sale order")
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
            partner_id.latest_followup_level_id.block_sale and \
            partner_id.latest_followup_level_id) or \
            (partner_id.parent_id and \
            partner_id.parent_id.latest_followup_level_id and \
            partner_id.parent_id.latest_followup_level_id.block_sale and \
            partner_id.parent_id.latest_followup_level_id)
        manager = self.user_has_groups(cr, uid,
            'account_followup_block_invoice.group_invoice_followup_manager', context=context)
        if opposition and not manager:
            raise orm.except_orm(_('Warning!'),
                _('You cannot confirm an invoice for a customer '
                  'with follow up %s.\nAsk one of the accounting manager '
                  'to confirm this invoice.')
                % (opposition.name))

    def check_partner_followup(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            partner_id = invoice.partner_id
            if partner_id:
                self._check_partner_followup(cr, uid, partner_id, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: