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
from openerp import SUPERUSER_ID
from openerp.osv.orm import browse_null

class sale_configurable(orm.Model):
    _name = 'sale.configurable'
    _description = 'Sale configurable confirmation'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'field_to_test': fields.char('Field to test', size=256,
            required=True, help="Choose here the field name to test"),
        'test': fields.selection([
            ('<', '<'),
            ('<=', '<='),
            ('>', '>'),
            ('>=', '>='),
            ('=', '='),
            ('!=', '!='),
            ('is_set', 'Is set'),
            ('is_not_set', 'Is not set'),
            ], string='Test', required=True),
        'value_to_test': fields.char('Value to test', size=256,
            help="Choose the value to test.\n" \
                 "Enter the fixed value if fixed, " \
                 "or set the field to test if variable"),
        'type_to_test': fields.selection([
            ('fixed', 'Fixed'),
            ('variable', 'Variable')
            ], string='Type of value tested', required=True),
        'warning': fields.boolean('Warning'),
        'warning_to_print': fields.text('Warning to print', translate=True,
            help="You can choose to display some specific " \
                 "data related to some value.\n" \
                 "Put %s in the text to print it."),
        'warning_value_to_print': fields.char('Value to print', size=512,
            help="Choose here the value you want to print " \
                 "to replace the %s.\n" \
                 "You can get many values. You should just " \
                 "separate them with ',' and no space"),
        'block': fields.boolean('Blocked'),
        'block_to_print': fields.text('Text to print', translate=True,
            help="You can choose to display some specific " \
                 "data related to some value.\n" \
                 "Put %s in the text to print it."),
        'block_value_to_print': fields.char('Value to print', size=512,
            help="Choose here the value you want to print " \
                 "to replace the %s.\n" \
                 "You can get many values. You should just " \
                 "separate them with ',' and no space"),
        'groups': fields.many2many('res.groups',
                                   'ir_sale_configurable_group_rel',
                                   'config_id', 'group_id', 'Groups'),
        'company_id': fields.many2one('res.company', 'Company'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
        'type_to_test': 'fixed',
    }

class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _get_object_value(self, cr, uid, obj, field, context=None):
        if context is None:
            context = {}
        if obj.__getitem__(field) is not None:
            obj = obj.__getitem__(field)
        return obj

    def _test_value(self, cr, uid, obj,
                    blocking, base_obj,
                    value_to_test, context=None):
        if context is None:
            context = {}
        test = blocking.test
        if not test in ('is_set', 'is_not_set'):
            if blocking.type_to_test == 'variable':
                values_to_test = value_to_test.split('.')
                value = base_obj
                for field in values_to_test:
                    value = self._get_object_value(
                        cr, uid, value, field, context=context)
            else:
                value = value_to_test
        else:
            if test == 'is_set':
                if obj != True and obj != None and \
                    obj != [] and obj != 0 and \
                    obj != '' and type(obj) != browse_null:
                    return False
            elif test == 'is_not_set':
                if obj == False or obj == None or \
                    obj == [] or obj == 0 or obj == '' or \
                    type(obj) == browse_null:
                    return False
            return True
        if value in ('True', 'true', 'False', 'false'):
            if value in ('True', 'true'):
                value = True
            else:
                value = False
        if not isinstance(value, type(obj)):
            try:
                value = type(obj)(value)
            except Exception:
                return True
        if test == '<':
            if obj < value:
                return False
        elif test == '<=':
            if obj <= value:
                return False
        elif test == '>':
            if obj > value:
                return False
        elif test == '>=':
            if obj >= value:
                return False
        elif test == '=':
            if obj == value:
                return False
        elif test == '!=':
            if obj != value:
                return False
        return True

    def _value_display(self, cr, uid, current, blocking,
                       to_print, value_to_print,
                       context=None):
        if context is None:
            context = {}
        to_display = to_print
        vals = []
        if value_to_print:
            vals = value_to_print.split(',')
        values = []
        if vals:
            for val in vals:
                obj = current
                value = ''
                value_to_test = val.split('.')
                for field in value_to_test:
                    obj = self._get_object_value(
                        cr, uid, obj, field, context=context)
                if not isinstance(obj, (str, unicode, float, int, long, bool)):
                    value = ''
                else:
                    value = str(obj)
                values.append(value)
            count = to_display.count('%s')
            if count > len(values):
                while count > len(values):
                    values.append('')
            elif count < len(values):
                while count < len(values):
                    values.pop()
            to_display = to_display % tuple(values)
        return to_display

    def _check_if_validable(self, cr, uid, sale, context=None):
        if context is None:
            context = {}
        confirmation_obj = self.pool.get('sale.configurable')
        blocking_ids = confirmation_obj.search(cr, uid, [
                '|', ('company_id', '=', False),
                ('company_id', '=', sale.company_id.id),
                ('block', '=', True),
            ], context=context)
        user_obj = self.pool.get('res.users')
        group_ids = [x.id for x in 
            user_obj.browse(cr, SUPERUSER_ID,
                            uid, context=context).groups_id]
        for blocking in confirmation_obj.browse(cr, uid,
                                                blocking_ids,
                                                context=context):
            stop = False
            valid_group_ids = [x.id for x in blocking.groups]
            for group in valid_group_ids:
                if group in group_ids:
                    stop = True
            if stop:
                continue
            if blocking.block:
                fields_to_test = blocking.field_to_test.split('.')
                obj = sale
                for field in fields_to_test:
                    obj = self._get_object_value(
                        cr, uid, obj, field, context=context)
                    if field == 'partner_id' and \
                        obj and obj.__hasattr__('parent_id'):
                        if obj.__getitem__('parent_id'):
                            obj = obj.__getitem__('parent_id')
                if not self._test_value(cr, uid, obj,
                                        blocking, sale,
                                        blocking.value_to_test,
                                        context=context):
                    to_display = self._value_display(cr, uid,
                        sale, blocking, blocking.block_to_print,
                        blocking.block_value_to_print, context=context)
                    raise orm.except_orm(_('Warning'), to_display)
        return True

    def action_button_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for sale in self.browse(cr, uid, ids, context=context):
            self._check_if_validable(cr, uid, sale, context=context)
        return super(sale_order,
            self).action_button_confirm(cr, uid, ids, context=context)

    def onchange_partner_id(self, cr, uid,
            ids, part=False, context=None):
        warning = {}
        result = super(sale_order,
            self).onchange_partner_id(
            cr, uid, ids, part=part, context=context)
        warning_msgs = result.get('warning') and \
            result['warning']['message'] or ''
        warning_title = result.get('warning') and \
            result['warning']['title'] or ''
        confirmation_obj = self.pool.get('sale.configurable')
        if part:
            partner_obj = self.pool.get('res.partner')
            partner = partner_obj.browse(cr, uid, part, context=context)
            blocking_ids = confirmation_obj.search(cr, uid, [
#                    '|', ('company_id', '=', False),
#                    ('company_id', '=', sale.company_id.id),
                    ('warning', '=', True),
                ], context=context)
            for blocking in confirmation_obj.browse(cr, uid,
                                                    blocking_ids, context=context):
                if blocking.warning:
                    fields_to_test = blocking.field_to_test.split('.')
                    obj = partner
                    for field in fields_to_test:
                        if field == 'partner_id':
                            continue
                        if obj and obj.__hasattr__('parent_id'):
                            if obj.__getitem__('parent_id'):
                                obj = obj.__getitem__('parent_id')
                        obj = self._get_object_value(cr, uid, obj, field, context=context)
                    value_to_test = blocking.value_to_test
                    if value_to_test.startswith('partner_id'):
                        value_to_test = value_to_test.replace('partner_id.', '', 1)
                    if not self._test_value(cr, uid, obj,
                                            blocking, partner.parent_id or partner,
                                            value_to_test, context=context):
                        to_display = self._value_display(cr, uid,
                            partner.parent_id or partner, blocking,
                            blocking.warning_to_print,
                            blocking.warning_value_to_print, context=context)
                        if not warning_title:
                            warning_title = _('Warning!')
                        warning_msgs += to_display + '\n'
        if warning_msgs:
            warning = {
               'title': warning_title,
               'message': warning_msgs,
            }
            result.update({'warning': warning})
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
