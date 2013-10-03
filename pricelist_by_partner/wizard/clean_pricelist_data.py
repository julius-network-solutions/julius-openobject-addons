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
from openerp import pooler

class clean_pricelist_data(orm.TransientModel):
    _name = 'clean.pricelist.data'
    
    _columns = {}
    
    def clean_pricelist_data(self, cr, uid, ids, context=None):
        version_obj = self.pool.get('product.pricelist.version')
        version_ids = version_obj.search(cr, uid,
            [('active', '=', False)], context=context)
        if version_ids:
            version_obj.unlink(cr, uid, version_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def _update_object(self, cr, uid, object, field, ids, context=None):
        if len(ids) == 1:
            where = ' WHERE id = %s;' % (str(ids[0]))
        else:
            where = ' WHERE id IN %s;' % (str(tuple(ids)))
        request = 'UPDATE %s SET %s = FALSE %s' %(object, field, where)
        return cr.execute(request)

    def _get_category_domain_sale(self, cr, uid, context=None):
        return [('list_to_compute_sale', '=', True)]

    def _get_partner_domain_sale(self, cr, uid, context=None):
        return [
            '|', ('is_company', '=', True),
            ('parent_id', '=', False),
            ('list_to_compute_sale', '=', True),
        ]

    def _get_category_domain_purchase(self, cr, uid, context=None):
        return [('list_to_compute_purchase', '=', True)]

    def _get_partner_domain_purchase(self, cr, uid, context=None):
        return [
            '|', ('is_company', '=', True),
            ('parent_id', '=', False),
            ('list_to_compute_purchase', '=', True),
        ]
    
    def _update_list_price(self, cr, uid, obj,
                           domain, type, list_type, context=None):
        item_obj = self.pool.get('product.pricelist.items.partner')
        list_ids = obj.search(cr, uid, domain, limit=10, context=context)
        item_obj._create_update_pricelist(cr, uid, list_ids,
                                          type=type, context=context)
        if type == 'category':
            model = 'res_partner_category'
        elif type == 'partner':
            model = 'res_partner'
        else:
            return []
        if list_type == 'sale':
            field = 'list_to_compute_sale'
        elif list_type == 'purchase':
            field = 'list_to_compute_purchase'
        else:
            return []
        if list_ids:
            self._update_object(cr, uid, model,
                                field, list_ids, context=context)
        cr.commit()
        return list_ids
    
    def create_pricelist_sale_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context['type'] = 'sale'
        category_obj = self.pool.get('res.partner.category')
        partner_obj = self.pool.get('res.partner')
        domain = self._get_category_domain_sale(cr, uid, context=context)
        while True:
            list_ids = self._update_list_price(cr, uid,
                category_obj, domain, type='category', list_type='sale', context=context)
            if not list_ids:
                break
        domain = self._get_partner_domain_sale(cr, uid, context=context)
        while True:
            list_ids = self._update_list_price(cr, uid,
                partner_obj, domain, type='partner', list_type='sale', context=context)
            if not list_ids:
                break
        return {'type': 'ir.actions.act_window_close'}
    
    def create_pricelist_purchase_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context['type'] = 'purchase'
        category_obj = self.pool.get('res.partner.category')
        partner_obj = self.pool.get('res.partner')
        domain = self._get_category_domain_purchase(cr, uid, context=context)
        while True:
            list_ids = self._update_list_price(cr, uid,
                category_obj, domain, type='category', list_type='purchase', context=context)
            if not list_ids:
                break
        domain = self._get_partner_domain_purchase(cr, uid, context=context)
        while True:
            list_ids = self._update_list_price(cr, uid,
                partner_obj, domain, type='partner', list_type='purchase', context=context)
            if not list_ids:
                break
        return {'type': 'ir.actions.act_window_close'}

    def _clean_pricelist_data(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        if context is None:
            context = {}
        try:
            if use_new_cursor:
                cr = pooler.get_db(use_new_cursor).cursor()
            self.clean_pricelist_data(cr, uid, ids, context=context)
            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return {}

    def _create_pricelist_sale_data(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        if context is None:
            context = {}
        try:
            if use_new_cursor:
                cr = pooler.get_db(use_new_cursor).cursor()
            self.create_pricelist_sale_data(cr, uid, ids, context=context)
            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return {}

    def _create_pricelist_purchase_data(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        if context is None:
            context = {}
        try:
            if use_new_cursor:
                cr = pooler.get_db(use_new_cursor).cursor()
            self.create_pricelist_purchase_data(cr, uid, ids, context=context)
            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return {}

    def run_generator(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        ''' Runs through scheduler.
        @param use_new_cursor: False or the dbname
        '''
        if use_new_cursor:
            use_new_cursor = cr.dbname
        self._clean_pricelist_data(cr, uid, use_new_cursor=use_new_cursor, context=context)
        self._create_pricelist_sale_data(cr, uid, use_new_cursor=use_new_cursor, context=context)
        self._create_pricelist_purchase_data(cr, uid, use_new_cursor=use_new_cursor, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
