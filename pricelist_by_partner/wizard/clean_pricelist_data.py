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

class clean_pricelist_data(orm.Model):
    _name = 'clean.pricelist.data'
    
    _columns = {}
    
    def clean_pricelist_data(self, cr, uid, ids, context=None):
        version_obj = self.pool.get('product.pricelist.version')
        version_ids = version_obj.search(cr, uid,
            [('active', '=', False)], context=context)
        if version_ids:
            version_obj.unlink(cr, uid, version_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
    
    def create_pricelist_sale_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context['type'] = 'sale'
        category_obj = self.pool.get('res.partner.category')
        partner_obj = self.pool.get('res.partner')
        item_obj = self.pool.get('product.pricelist.items.partner')
        while True:
            category_ids = category_obj.search(cr, uid, [
                ('list_to_compute_sale', '=', True),
            ], limit=10, context=context)
            item_obj._create_update_pricelist(cr, uid, category_ids,
                                              type='category', context=context)
            if category_ids:
                cr.execute("UPDATE res_partner_category SET list_to_compute_sale = FALSE WHERE id IN %s;" % (str(tuple(category_ids))))
            cr.commit()
            if not category_ids:
                break
        offset = 0
        while True:
            partner_ids = partner_obj.search(cr, uid, [
                ('is_company', '=', True),
                ('list_to_compute_sale', '=', True),
            ], limit=10, context=context)
            item_obj._create_update_pricelist(cr, uid, partner_ids,
                                              type='partner', context=context)
            if partner_ids:
                partner_obj.write(cr, uid, partner_ids,
                                  {'list_to_compute_sale': False}, context=context)
            if partner_ids:
                cr.execute("UPDATE res_partner SET list_to_compute_sale = FALSE WHERE id IN %s;" % (str(tuple(partner_ids))))
            cr.commit()
            if not partner_ids:
                break
        return {'type': 'ir.actions.act_window_close'}
    
    def create_pricelist_purchase_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context['type'] = 'purchase'
        category_obj = self.pool.get('res.partner.category')
        partner_obj = self.pool.get('res.partner')
        item_obj = self.pool.get('product.pricelist.items.partner')
        while True:
            category_ids = category_obj.search(cr, uid, [
                ('list_to_compute_purchase', '=', True),
            ], limit=10, context=context)
            item_obj._create_update_pricelist(cr, uid, category_ids,
                                              type='category', context=context)
            if category_ids:
                cr.execute("UPDATE res_partner_category SET list_to_compute_purchase = FALSE WHERE id IN %s;" % (str(tuple(complete_ids))))
            cr.commit()
            if not category_ids:
                break
        while True:
            partner_ids = partner_obj.search(cr, uid, [
                ('is_company', '=', True),
                ('list_to_compute_purchase', '=', True),
            ], limit=10, context=context)
            item_obj._create_update_pricelist(cr, uid, partner_ids,
                                              type='partner', context=context)
            if partner_ids:
                cr.execute("UPDATE res_partner SET list_to_compute_purchase = FALSE WHERE id IN %s;" % (str(tuple(partner_ids))))
            cr.commit()
            if not partner_ids:
                break
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
