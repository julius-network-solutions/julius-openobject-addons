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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp

class product_pricelist(orm.Model):
    _inherit = 'product.pricelist'
    
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
    }
    
class product_pricelist_items_partner(orm.Model):
    _description = 'Pricelist items by partner'
    _name = 'product.pricelist.items.partner'

    def _pricelist_type_get(self, cr, uid, context=None):
        pricelist_type_obj = self.pool.get('product.pricelist.type')
        pricelist_type_ids = pricelist_type_obj.search(cr, uid, [], order='name')
        pricelist_types = pricelist_type_obj.read(cr, uid, pricelist_type_ids, ['key','name'], context=context)
        res = []
        for type in pricelist_types:
            res.append((type['key'],type['name']))
        return res
    
    _columns = {
        'name': fields.char('Name', size=128),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'partner_category_id': fields.many2one('res.partner.category', 'Partner category'),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_category_id': fields.many2one('product.category', 'Product category'),
        'min_quantity': fields.integer('Min. Quantity', required=True,
            help="Specify the minimum quantity that needs to be bought/sold for the rule to apply."),
        'discount': fields.float('Discount (%)', digits=(16,4)),
        'price': fields.float('Price', digits_compute= dp.get_precision('Product Price')),
        'date_start': fields.date('Date Start'),
        'date_end': fields.date('Date End'),
        'type': fields.selection(_pricelist_type_get, 'Pricelist Type', required=True),
    }
    
    _defaults = {
        'min_quantity': lambda *a: 0,
        'discount': lambda *a: 0,
        'type': 'sale',
    }
    
    def onchange_product_id(self, cr, uid, ids, product_id=False, product_category_id=False, 
            partner_id=False, partner_category_id=False, date_start=False, date_end=False, context=None):
        if context is None:
            context = {}
        result = {}
        list_type = context.get('type') or 'sale'
        partner_id = partner_id or context.get('partner_id') or False
        partner_category_id = partner_category_id or context.get('partner_category_id') or False
        
        if (not product_id and not product_category_id) or (not partner_id and not partner_category_id):
            return result
        warning = {}
        warning_msgs = ''
        partner_obj = self.pool.get('res.partner')
        args = [('type', '=', list_type)]
        if ids:
            args.append(('id', 'not in', ids))
        if product_id:
            args.append(('product_id', '=', product_id))
            warning_msgs = ('These dates overlap another pricelist item with the same product.')
        elif product_category_id:
            args.append(('product_category_id', '=', product_category_id))
            warning_msgs = ('These dates overlap another pricelist item with the same product_category.')
        if partner_id:
            args.append(('partner_id', '=', partner_id))
        elif partner_category_id:
            args.append(('partner_category_id', '=', partner_category_id))
        if not date_start and not date_end:
            args2 = []
        elif date_start and not date_end:
            args2 = [
                '|', '&', '|', ('date_start', '>=', date_start), ('date_start', '=', False),
                '|', ('date_end', '>=', date_start), ('date_end', '=', False),
                '&', ('date_start', '<=', date_start), ('date_end', '>=', date_start),
            ]
        elif not date_start and date_end:
            args2 = [
                '|', '&', '|', ('date_start', '<=', date_end), ('date_start', '=', False),
                '|', ('date_end', '<=', date_end), ('date_end', '=', False),
                '&', ('date_start', '<=', date_end), ('date_end', '>=', date_end),
            ]
        else:
            args2 = [
                '|', '&', '|', ('date_start', '<=', date_end), ('date_start', '=', False),
                '|', ('date_end', '>=', date_start), ('date_end', '=', False),
                '&', ('date_start', '<=', date_end), ('date_end', '>=', date_start)
            ]
        args += args2
#        ### Process ###
#        for current_item in self.browse(cr, uid, ids):
#            partner_pricelist_item_ids = partner_obj.browse(cr, uid, partner_id).pricelist_items_ids
#            for pricelist_item in partner_pricelist_item_ids:
#                if pricelist_item.product_id.id != product_id:
#                    continue
#                ### No Date in the record ###
#                if not pricelist_item.date_start and not pricelist_item.date_end:
#                    warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
#                ### No Start Date ###
#                elif not pricelist_item.date_start:
#                    if context.get('date_end') < pricelist_item.date_end or context.get('date_start') < pricelist_item.date_end:
#                        warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
#                ### No End Date ###
#                elif not pricelist_item.date_end:
#                    if context.get('date_end') > pricelist_item.date_start or context.get('date_start') > pricelist_item.date_start:
#                        warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
#                ### No Date in current item ###
#                elif not context.get('date_start') and not context.get('date_end'):
#                    warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
#                ### No Date Start in current item ###
#                elif not context.get('date_start'):
#                    if pricelist_item.date_start < context.get('date_end') or pricelist_item.date_end < context.get('date_end'):
#                        warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
#                ### No Date End in current item ###
#                elif not context.get('date_end'):
#                    if pricelist_item.date_start > context.get('date_start') or pricelist_item.date_end > context.get('date_start'):
#                        warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
#                ### All date in the system ###
#                elif context.get('date_end') > pricelist_item.date_end and context.get('date_start') < pricelist_item.date_end:
#                    warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
#                elif context.get('date_start') < pricelist_item.date_start and context.get('date_end') > pricelist_item.date_start:
#                    warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
#                elif context.get('date_start') > pricelist_item.date_start and context.get('date_start') < pricelist_item.date_end:
#                    warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
#                elif context.get('date_end') > pricelist_item.date_start and context.get('date_end') < pricelist_item.date_end:
#                    warning_msgs = ('These dates overlap another pricelist item with the same product.\n')
        if self.search(cr, uid, args, limit=1):
#        ### End of On_change display result ###
#        if warning_msgs:
            warning = {
                       'title': _('Input Error!'),
                       'message' : warning_msgs
                    }
        result = {'warning': warning}
        return result
    
    def _check_date(self, cursor, user, ids, context=None):
        if context is None:
            context = {}
        for pricelist_partner_item in self.browse(cursor, user, ids, context=context):
            if (not pricelist_partner_item.partner_id and not pricelist_partner_item.partner_category_id) \
                or (not pricelist_partner_item.product_id and not pricelist_partner_item.product_category_id):
                continue
            where = []
            if pricelist_partner_item.date_start:
                where.append("((date_end>='%s') or (date_end is null))" % (pricelist_partner_item.date_start,))
            if pricelist_partner_item.date_end:
                where.append("((date_start<='%s') or (date_start is null))" % (pricelist_partner_item.date_end,))
            request = 'SELECT id ' \
                    'FROM product_pricelist_items_partner ' \
                    'WHERE '+' AND '.join(where) + (where and ' AND ' or '') + \
                        'id <> ' + str(pricelist_partner_item.id)
            if pricelist_partner_item.partner_id:
                request += ' AND partner_id = ' + str(pricelist_partner_item.partner_id.id)
            elif pricelist_partner_item.partner_category_id:
                request += ' AND partner_category_id = ' + str(pricelist_partner_item.partner_category_id.id)
            if pricelist_partner_item.product_id:
                request += ' AND product_id = ' + str(pricelist_partner_item.product_id.id)
            elif pricelist_partner_item.product_category_id:
                request += ' AND product_category_id = ' + str(pricelist_partner_item.product_category_id.id)
            if pricelist_partner_item.min_quantity:
                request += " AND min_quantity = " + str(pricelist_partner_item.min_quantity)
            else:
                request += " AND (min_quantity IS NULL or min_quantity = 0) "
            request += " AND type = '" + str(pricelist_partner_item.type) + "'"
            cursor.execute(request)
            if cursor.fetchall():
                return False
        return True

    def _check_dates_start_end(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids, context=context):
            if item.date_start and item.date_end and item.date_start > item.date_end:
                return False
        return True

    _constraints = [
        (_check_date, 'You cannot have 2 pricelist items that overlap!',
            ['date_start', 'date_end']),
        (_check_dates_start_end, "Pricelist item 'Date Start' must be before 'Date End'.", ['date_start', 'date_end'])
    ]
    
class res_partner_category(orm.Model):
    _inherit = "res.partner.category"
    
    _columns = {
        'pricelist_items_ids': fields.one2many('product.pricelist.items.partner', 'partner_category_id',
                                               'Defined price', domain=[('type', '=', 'sale')]),
        'pricelist_items_purchase_ids': fields.one2many('product.pricelist.items.partner', 'partner_category_id',
                                                        'Defined price', domain=[('type', '=', 'purchase')]),
    }

class res_partner(orm.Model):
    _inherit = "res.partner"
    
    def _get_all_pricelist_items(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        partners = self.browse(cr, uid, ids, context=context)
        res = {}
        for partner in partners:
            res[partner.id] = [x.id for x in partner.pricelist_items_ids]
            for categ in partner.category_id:
                for item in categ.pricelist_items_ids:
                    if item.type == 'sale':
                        res[partner.id].append(item.id)
        return res
    
    def _get_all_pricelist_purchase_items(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        partners = self.browse(cr, uid, ids, context=context)
        res = {}
        for partner in partners:
            res[partner.id] = [x.id for x in partner.pricelist_items_purchase_ids]
            for categ in partner.category_id:
                for item in categ.pricelist_items_purchase_ids:
                    if item.type == 'purchase':
                        res[partner.id].append(item.id)
        return res
    
    _columns = {
        'pricelist_items_ids': fields.one2many('product.pricelist.items.partner',
                'partner_id', 'Defined sale price', domain=[('type', '=', 'sale')]),
        'complete_pricelist_items_ids': fields.function(_get_all_pricelist_items,
            method=True, type='one2many', obj='product.pricelist.items.partner', string='Defined sale price'),
        'pricelist_items_purchase_ids': fields.one2many('product.pricelist.items.partner',
                'partner_id', 'Defined purchase price', domain=[('type', '=', 'purchase')]),
        'complete_pricelist_items_purchase_ids': fields.function(_get_all_pricelist_purchase_items,
            method=True, type='one2many', obj='product.pricelist.items.partner', string='Defined purchase price'),
    }
    
    def _get_pricelist_version_vals(self, cr, uid, pricelist_id,
            partner, date_start=False, date_end=False, context=None):
        return {
            'name': partner.name + ' ' + _('Version'),
            'date_start': date_start,
            'date_end': date_end,
            'pricelist_id': pricelist_id,
        }
        
    def _create_default_pricelist_item(self,
            cr, uid, version_id, partner, context=None):
        """ This method can be called if you want to create
        a price list item which tells the system everything is 
        the price of the main price list.
        """
        if context is None:
            context = {}
        data_obj = self.pool.get('ir.model.data')
        pricelist_item_obj = self.pool.get('product.pricelist.item')
        list_type = context.get('type') or 'sale'
        if list_type == 'purchase':
            main_pricelist_id = data_obj.get_object(cr, uid, 'purchase', 'list0').id
        else:
            main_pricelist_id = data_obj.get_object(cr, uid, 'product', 'list0').id
        pricelist_item_obj.create(cr, uid, {
                'price_version_id': version_id,
                'base_pricelist_id': main_pricelist_id,
                'sequence': 1000,
                'name': partner.name + ' ' + _('Item'),
            }, context=context)
        return True
    
    def _get_base_item_id(self, cr, uid, context=None):
        data_obj = self.pool.get('ir.model.data')
        base_id = data_obj.get_object(cr, uid, 'product', 'list_price').id
        return base_id
    
    def _get_discount_value(self, cr, uid, item, context=None):
        return item.discount and (- item.discount / 100) or False

    def _get_item_sequence(self, cr, uid, item, partner, context=None):
        return item.partner_category_id and 100 or 1

    def _create_pricelist_items(self, cr, uid, 
            version_id, partner, pricelist_items,
            date_start=False, date_end=False, context=None):
        """ This method can be called if you want to create
        a price list item which tells the system everything is 
        the price of the main price list.
        """
        if context is None:
            context = {}
        pricelist_item_obj = self.pool.get('product.pricelist.item')
        for item in pricelist_items:
            create = False
            if not item.date_start and not item.date_end:
                create = True
            elif not date_start and not date_end:
                create = True
            elif item.date_start and not item.date_end:
                if date_start and not date_end:
                    if item.date_start <= date_start:
                        create = True
                elif not date_start and date_end:
                    if item.date_start <= date_end:
                        create = True
                elif date_start and date_end:
                    if item.date_start <= date_start:
                        create = True 
            elif not item.date_start and item.date_end:
                if date_start and not date_end:
                    if item.date_end >= date_start:
                        create = True
                elif not date_start and date_end:
                    if item.date_end >= date_end:
                        create = True
                elif date_start and date_end:
                    if item.date_end >= date_end:
                        create = True 
            elif item.date_start and item.date_end:
                if date_start and not date_end:
                    if item.date_end >= date_start:
                        create = True
                elif not date_start and date_end:
                    if item.date_start <= date_end:
                        create = True
                elif date_start and date_end:
                    if item.date_start <= date_end and item.date_end >= date_start:
                        create = True
            if create:
                base_id = self._get_base_item_id(cr, uid, context=context)
                seq = self._get_item_sequence(cr, uid, item, partner, context=context)
                min_quantity = item.min_quantity > 0 and item.min_quantity or 0
                discount = self._get_discount_value(cr, uid, item, context=context)
                price = item.price or False
                if price:
                    discount = -1
                pricelist_item_obj.create(cr, uid, {
                        'price_version_id': version_id,
                        'base': base_id,
                        'product_id': item.product_id and item.product_id.id or False,
                        'categ_id': item.product_category_id and item.product_category_id.id or False,
                        'min_quantity': min_quantity,
                        'price_discount': discount,
                        'price_surcharge': price,
                        'sequence': seq,
                        'name': partner.name + ' ' + _('Item'),
                    }, context=context)
        return True

    def _get_dates_item_split(self, cr, uid, pricelist_items, context=None):
        if context is None:
            context = {}
        res = []
        res2 = []
        dates = []
        dates_start = []
        dates_end = []
        # These two in_start and in_end are used to know if we got data in
        # date start and date end and this is use only
        # if there is only 1 date defined
        in_start = False
        in_end = False
        same_dates = []

        #Here get all dates in the price list items
        for item in pricelist_items:
            date_start = item.date_start or False
            date_end = item.date_end or False
            res2.append((date_start,date_end))
            if date_start and date_start not in dates:
                dates.append(date_start)
            if date_start and date_start not in dates_start:
                dates_start.append(date_start)
            if date_end and date_end not in dates:
                dates.append(date_end)
            if date_end and date_end not in dates_end:
                dates_end.append(date_end)
        if dates_start:
            in_start = True
        if dates_end:
            in_end = True
        if len(dates) > 1:
            for date in dates_start:
                if date in dates_end:
                    same_dates.append(date)
        if not dates:
            # If there is no date we will return only an empty date value
            res.append((False,False))
        else:
            if len(dates) == 1:
                # If there is only 1 date:
                # We should have a specific type of date return
                if in_start:
                    date_inf = datetime.strptime(dates[0], DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=-1)
                    date_inf = date_inf.strftime(DEFAULT_SERVER_DATE_FORMAT)
                if in_end:
                    date_supp = datetime.strptime(dates[0], DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=1)
                    date_supp = date_supp.strftime(DEFAULT_SERVER_DATE_FORMAT)
                if in_start and in_end:
                    # If this date is defined in start and in end dates
                    res = [(False, date_inf), (dates[0], dates[0]), (date_supp, False)]
                else:
                    if in_start:
                        res = [(False,date_inf),(dates[0],False)]
                    else:
                        res = [(False,dates[0]),(date_supp,False)]
            else:
                # If there are, return a list of tuple
                # We shouldn't have any date which overlapped
                res2 = sorted(res2)
                dates = sorted(dates, reverse=True)
                # The first date is this one
                first_date = dates.pop()
                first_date_inf = datetime.strptime(first_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=-1)
                first_date_inf = first_date_inf.strftime(DEFAULT_SERVER_DATE_FORMAT)
                # The first tuple will be (False, first date - 1 day)
                res.append((False, first_date_inf))
                force_add_start = False
                while len(dates):
                    next_date = dates.pop()
                    next_date_inf = False
                    add_start = True
                    remove_end = True
                    for date_start, date_end in res2:
                        if date_end:
                            end = min(next_date, date_end)
                        else:
                            end = next_date
                        if first_date == date_start:
                            add_start = False
                        if next_date == date_end:
                            remove_end = False
                    if add_start or force_add_start:
                        first_date = datetime.strptime(first_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=1)
                        first_date = first_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                        force_add_start = False
                    if remove_end:
                        end = datetime.strptime(end, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=-1)
                        end = end.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    if first_date >= end:
                        end = first_date
                        force_add_start = True
                    res.append((first_date, end))
                    first_date = end
                first_date_supp = datetime.strptime(first_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=1)
                first_date_supp = first_date_supp.strftime(DEFAULT_SERVER_DATE_FORMAT)
                # The last tuple will be (last date + 1 day, False)
                res.append((first_date_supp,False))
                # This part is done to fix issues due to date which are
                # define both in date start and date end
                if same_dates:
                    res3 = res
                    res = []
                    for date_start, date_end in res3:
                        if date_start == date_end and not (date_start,date_end) in res:
                            res.append((date_start,date_end))
                        elif date_end in same_dates:
                            start = date_end
                            end = date_end
                            end_date = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=-1)
                            end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                            if not (start,end) in res:
                                res.append((date_start,end_date))
                                res.append((start,end))
                        elif date_start in same_dates:
                            start = date_start
                            end = date_start
                            if not (start,end) in res:
                                res.append((start,end))
                            first_date = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=1)
                            first_date = first_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                            date_start = first_date
                            res.append((date_start,date_end))
                        else:
                            res.append((date_start,date_end))
        return res
    
    def _create_pricelist_version(self, cr, uid, pricelist_id,
            partner, context=None):
        """ This method will unactivate all the versions of a pricelist, then
        create versions with infos defined in items in the partner view """
        if context is None:
            context = {}
        pricelist_obj = self.pool.get('product.pricelist')
        pricelist_version_obj = self.pool.get('product.pricelist.version')
        version_ids = pricelist_version_obj.search(cr, uid, [
                ('pricelist_id', '=', pricelist_id),
            ], context=context)
        if version_ids:
            pricelist_version_obj.write(cr, uid, version_ids, {'active': False}, context=context)
        items = []
        if context.get('type') == 'purchase':
            items = partner.complete_pricelist_items_purchase_ids
        else:
            items = partner.complete_pricelist_items_ids
        if not items:
            # If there is no items defined in the partner
            # We just create a simple price list version without date
            # and an item which is linked to the main price list
            vals = self._get_pricelist_version_vals(cr,
                uid, pricelist_id, partner, context=context)
            version_id = pricelist_version_obj.create(cr, uid, vals, context=context)
            self._create_default_pricelist_item(cr, uid, version_id, partner, context=context)
        else:
            dates = self._get_dates_item_split(cr, uid, items, context=context)
            for date_start, date_end in dates:
                vals = self._get_pricelist_version_vals(cr,
                    uid, pricelist_id, partner,date_start=date_start,
                    date_end=date_end, context=context)
                version_id = pricelist_version_obj.create(cr, uid, vals, context=context)
                self._create_default_pricelist_item(cr, uid, version_id, partner, context=context)
                self._create_pricelist_items(cr, uid, version_id,
                    partner, items,
                    date_start, date_end, context=context)
        return True

    def _get_vals_for_price_list(self, cr, uid, partner, list_type, context=None):
        if context is None:
            context = {}
        return {
            'name': partner.name + ' ' + _('List price'),
            'partner_id': partner.id,
            'type': list_type,
        }

    def _create_update_pricelist(self, cr, uid, ids, context=None):
        """ This method will create a pricelist for Partners if there is no pricelist
        which is linked to this partner """
        if context is None:
            context = {}
        list_type = context.get('type') or 'sale'
        pricelist_obj = self.pool.get('product.pricelist')
        for partner in self.browse(cr, uid, ids, context=context):
            parent = partner.parent_id
            if not parent:
                vals = self._get_vals_for_price_list(cr, uid,
                    partner, list_type, context=context)
                # If there's no parent company we create a pricelist for the partner
                pricelist_ids = pricelist_obj.search(cr, uid, [
                        ('partner_id', '=', partner.id),
                        ('type', '=', list_type)
                    ], limit=1, context=context)
                if not pricelist_ids:
                    pricelist_id = pricelist_obj.create(cr, uid, vals, context=context)
                else:
                    pricelist_id = pricelist_ids[0]
                    pricelist_obj.write(cr, uid, pricelist_id, vals, context=context)
                if list_type == 'purchase':
                    self.write(cr, uid, partner.id, {
                            'property_product_pricelist_purchase': pricelist_id
                        }, context=context)
                else:
                    self.write(cr, uid, partner.id, {
                            'property_product_pricelist': pricelist_id
                        }, context=context)
                self._create_pricelist_version(cr, uid, pricelist_id, partner, context=context)
        return True
    
    def create_update_pricelist(self, cr, uid, ids, context=None):
        self._create_update_pricelist(cr, uid, ids, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
