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
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class subscription_document_fields(orm.Model):
    _inherit = "subscription.document.fields"
    _description = "Subscription Document Fields"

    def _get_value_selection(self, cr, uid, context=None):
        value_selection = super(subscription_document_fields,
                                self)._get_value_selection(cr, uid,
                                                           context=context)
        value_selection.append(('start_date', 'Start Date'))
        value_selection.append(('end_date', 'End Date'))
        return value_selection

    _columns = {
        'value': fields.selection(_get_value_selection, 'Default Value', size=40,
                                  help="Default value is considered for " \
                                  "field when new document is generated."),
    }

class subscription_subscription(orm.Model):
    _inherit = "subscription.subscription"
    _description = "Subscription"
    
    _columns = {
        'first_day': fields.integer('First day',
            help="This field is used to be able to specify " \
            "the first day of the subscription and also " \
            "to be able to compute the last day of the subscription"),
    }
    
    _defaults = {
        'first_day': 1,
    }

    def _get_specific_defaut_values(self, cr, uid, id, f, context=None):
        if context is None:
            context = {}
        value = super(subscription_subscription,
            self)._get_specific_defaut_values(cr, uid, id, f, context=context)
        if f.value in ('start_date', 'end_date'):
            read_value = self.read(cr, uid, id, [
                'interval_number',
                'interval_type',
                'first_day',
                ], context=context)
            first_day = read_value.get('first_day')
            interval_number = read_value.get('interval_number')
            interval_type = read_value.get('interval_type')
            date = datetime.datetime.today()
            if first_day and interval_type == 'months':
                year = date.year
                month = date.month
                day = first_day
                date = datetime.date(
                    year=year, month=month, day=day)
            if f.value == 'end_date':
                months = 0
                days = -1
                if interval_type == 'months':
                    months = interval_number
                elif interval_type == 'weeks':
                    days += 7 * interval_number
                else:
                    days += interval_number
                date += relativedelta(months=months, days=days)
            value = date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        return value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
