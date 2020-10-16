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

class sale_order(orm.Model):
    _inherit = 'sale.order'

    def onchange_partner_id(self, cr, uid, ids, part=False, context=None):
        warning = {}
        result = super(sale_order,
            self).onchange_partner_id(cr, uid, ids, part=part, context=context)
        warning_msgs = result.get('warning') and result['warning']['message'] or ''
        warning_title = result.get('warning') and result['warning']['title'] or ''
        if part:
            res_partner_obj = self.pool.get('res.partner')
            opposition = res_partner_obj.browse(
                cr, uid, part, context=context).admin_opposition
            if opposition:
                if not warning_title:
                    warning_title = _('Warning!')
                warn_msg = (_("This customer has got an admin opposition:"
                                 " %s\n") %opposition.name)
                if opposition.block_order:
                    warn_msg += _("You will not be able to confirm"
                                  " this sale order if you're not in the accounting"
                                  " department")
                else:
                   warn_msg += _("But, this opposition will not block the confirmation"
                                " of this sale order")
                warning_msgs += warn_msg
        if warning_msgs:
            warning = {
               'title': warning_title,
               'message' : warning_msgs,
            }
            result.update({'warning': warning})
        return result

    def action_button_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for sale in self.browse(cr, uid, ids, context=context):
            manager = self.user_has_groups(cr, uid,
                'sale_blocked.group_quotation_validate_manager', context=context)
            if sale.partner_id and sale.partner_id.admin_opposition and \
                sale.partner_id.admin_opposition.block_order and not manager:
                raise orm.except_orm(_('Warning!'),
                    _('You cannot confirm a sale order for a client with opposition %s.\n'
                      'Ask one of the accounting manager to confirm this sale.')
                    % (sale.partner_id.admin_opposition.name))
        return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: