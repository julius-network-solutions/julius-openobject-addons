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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class subscription_document_fields(orm.Model):
    _inherit = "subscription.document.fields"
    _description = "Subscription Document Fields"

    def _get_value_selection(self, cr, uid, context=None):
        value_selection = super(subscription_document_fields,
                                self)._get_value_selection(cr, uid,
                                                           context=context)
        value_selection.append(('partner', 'Partner'))
        return value_selection

    _columns = {
        'value': fields.selection(_get_value_selection, 'Default Value', size=40,
                                  help="Default value is considered for " \
                                  "field when new document is generated."),
    }

class subscription_subscription(orm.Model):
    _inherit = "subscription.subscription"
    _description = "Subscription"

    def _get_specific_defaut_values(self, cr, uid, id, f, context=None):
        if context is None:
            context = {}
        value = super(subscription_subscription,
            self)._get_specific_defaut_values(cr, uid, id, f, context=context)
        if f.value=='partner':
            read_value = self.read(cr, uid, id, ['partner_id'], context=context)
            if read_value.get('partner_id'):
                value = read_value.get('partner_id')[0]
        return value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
