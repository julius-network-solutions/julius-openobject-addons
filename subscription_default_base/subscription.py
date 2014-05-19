# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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

import time

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATETIME_FORMAT,
                           DEFAULT_SERVER_DATE_FORMAT)

class subscription_document_fields(orm.Model):
    _inherit = "subscription.document.fields"
    _description = "Subscription Document Fields"

    def _get_value_selection(self, cr, uid, context=None):
        return [('false','False'), ('date','Current Date')]
    
    _columns = {
        'value': fields.selection(_get_value_selection, 'Default Value',
                                  size=40,
                                  help="Default value is considered for " \
                                  "field when new document is generated."),
    }

class subscription_subscription(orm.Model):
    _inherit = "subscription.subscription"
    _description = "Subscription"

    _columns = {
        'document_id': fields.many2one("subscription.document",
                                       "Document type"),
    }

    def _get_specific_defaut_values(self, cr, uid, id, f, context=None):
        if context is None:
            context = {}
        value = False
        if f.value=='date':
            value = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        return value
    
    def _get_sub_document(self, cr, uid, row, model_name, context=None):
        if context is None:
            context = {}
        doc_obj = self.pool.get('subscription.document')
        document_ids = doc_obj.search(cr, uid, [
            ('model.model', '=', model_name)
            ], context=context)
        doc = doc_obj.browse(cr, uid, document_ids, context=context)[0]
        return doc

    def model_copy(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        cron_obj = self.pool.get('ir.cron')
        history_obj = self.pool.get('subscription.subscription.history')
        for row in self.browse(cr, uid, ids, context=context):
            if not row.cron_id:
                continue
            cron_ids = [row.cron_id.id]
            remaining = cron_obj.read(cr, uid, cron_ids,
                                      ['numbercall'])[0]['numbercall']
            try:
                doc_source = row.doc_source
                model_name = doc_source._name
                id = row.doc_source.id
                model = self.pool.get(model_name)
            except:
                raise orm.except_orm(_('Wrong Source Document!'),
                                     _('Please provide another source' \
                                       'document.\nThis one does not exist!'))

            default = {'state':'draft'}
            if row.document_id and row.document_id.model.model == model_name:
                doc = row.document_id
            else:
                doc = self._get_sub_document(cr, uid, row,
                                             model_name, context=context)
            for f in doc.field_ids:
                default[f.field.name] = self._get_specific_defaut_values(
                    cr, uid, row.id, f, context=context)

            state = 'running'

            # if there was only one remaining document to generate
            # the subscription is over and we mark it as being done
            if remaining == 1:
                state = 'done'
            id = self.pool.get(model_name).copy(cr, uid, id, default, context)
            history_obj.create(cr, uid, {
                'subscription_id': row.id,
                'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'document_id': model_name+','+str(id)
                }, context=context)
            self.write(cr, uid, [row.id], {'state': state}, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
