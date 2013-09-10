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
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for sale in self.browse(cr, uid, ids, context=context):
            manager = self.user_has_groups(cr, uid,
                'sale_blocked.group_quotation_validate_manager', context=context)
            if sale.partner_id.admin_opposition and not manager:
                raise orm.except_orm(_('WARNING!'),
                    _('You cannot confirm a sale order for a client with opposition %s.\n'
                      'Ask one of the accounting manager to confirm this sale.')
                    % (sale.partner_id.admin_opposition.name))
        return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: